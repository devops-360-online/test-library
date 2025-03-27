"""Main module providing the ObservabilityClient class."""

import atexit
import logging
import os
import socket
import time
from contextlib import contextmanager
from typing import Optional, Dict, Any, List, Callable, TypeVar, cast, Union, ContextManager

from opentelemetry import trace
from opentelemetry.trace import Span, Tracer, StatusCode

from .config import ObservabilityConfig
from .metrics import MetricsManager
from .logs import LogManager, DataLogger
from .traces import TraceManager
from .standards import (
    Environment, AttributeNames, MetricNames, LogLevel, 
    LogFormat, SpanNames, format_span_name
)

# Set up module logger
logger = logging.getLogger(__name__)

# Type variable for decorators
F = TypeVar('F', bound=Callable[..., Any])


class ObservabilityClient:
    """
    A simple client for managing application observability with OpenTelemetry.
    
    This class provides a unified interface for metrics, logs, and traces,
    making it easy to instrument data processing scripts with minimal
    configuration.
    """
    
    def __init__(
        self, 
        service_name: str,
        service_version: Optional[str] = None,
        environment: Optional[str] = None,
        prometheus_port: Optional[int] = None,
        log_level: Optional[int] = None,
        additional_attributes: Optional[Dict[str, Any]] = None,
        otlp_endpoint: Optional[str] = None,
        enable_console_export: Optional[bool] = None,
        json_logs: Optional[bool] = None,
        auto_shutdown: bool = True
    ):
        """
        Initialize the observability client with application information.
        
        Args:
            service_name: Name of the service/application
            service_version: Version of the service
            environment: Deployment environment (dev, staging, prod, etc.)
            prometheus_port: Port for Prometheus metrics scraping
            log_level: Default logging level
            additional_attributes: Any additional resource attributes
            otlp_endpoint: Optional OTLP exporter endpoint
            enable_console_export: Whether to enable console exporters for development
            json_logs: Whether to use JSON format for logs
            auto_shutdown: Register shutdown handler to clean up on exit
        """
        # Start by creating a configuration
        if all(arg is None for arg in [
            service_version, environment, prometheus_port, log_level, 
            otlp_endpoint, enable_console_export, json_logs
        ]):
            # If no configuration parameters are provided, load from environment
            self.config = ObservabilityConfig.from_env(service_name)
        else:
            # Apply environment-based defaults if not specified
            service_version = service_version or os.environ.get('SERVICE_VERSION', '0.1.0')
            
            # Use standardized environment names
            if environment is None:
                env = os.environ.get('ENVIRONMENT', Environment.DEVELOPMENT.value)
            else:
                # Try to map to standard environment names
                env_lower = environment.lower()
                if env_lower in ('dev', 'development'):
                    env = Environment.DEVELOPMENT.value
                elif env_lower in ('test', 'testing'):
                    env = Environment.TESTING.value
                elif env_lower in ('stage', 'staging'):
                    env = Environment.STAGING.value
                elif env_lower in ('prod', 'production'):
                    env = Environment.PRODUCTION.value
                else:
                    env = environment
                
            prometheus_port = prometheus_port or int(os.environ.get('PROMETHEUS_PORT', '8000'))
            log_level_str = os.environ.get('LOG_LEVEL', 'INFO')
            log_level = log_level or getattr(logging, log_level_str, logging.INFO)
            otlp_endpoint = otlp_endpoint or os.environ.get('OTLP_ENDPOINT')
            
            # Enable console export by default in development
            if enable_console_export is None:
                enable_console_export = env.lower() == Environment.DEVELOPMENT.value.lower()
                
            # Determine if we should use JSON logs
            if json_logs is None:
                json_logs = env.lower() == Environment.PRODUCTION.value.lower()
            
            # Add some common attributes
            hostname = socket.gethostname()
            extra_attrs = {
                AttributeNames.HOST_NAME: hostname,
            }
            if additional_attributes:
                extra_attrs.update(additional_attributes)
                
            # Create configuration
            self.config = ObservabilityConfig(
                service_name=service_name,
                service_version=service_version,
                environment=env,
                prometheus_port=prometheus_port,
                log_level=log_level,
                otlp_endpoint=otlp_endpoint,
                enable_console_export=enable_console_export,
                json_logs=json_logs,
                log_format=LogFormat.TRACE_CONTEXT if not json_logs else LogFormat.BASIC,
                additional_attributes=extra_attrs
            )
        
        # Initialize components
        logger.info(f"Initializing observability for service {service_name}")
        self.metrics = MetricsManager(self.config)
        self.logs = LogManager(self.config)
        self.traces = TraceManager(self.config)
        
        logger.info(f"Observability initialized for service {service_name}")
        
        # Register shutdown handler if requested
        if auto_shutdown:
            atexit.register(self.shutdown)
    
    #
    # Tracing API
    #
        
    def get_tracer(self, name: Optional[str] = None) -> Tracer:
        """
        Get a tracer instance for creating spans.
        
        Args:
            name: Name for the tracer, defaults to service name
            
        Returns:
            A tracer instance
        """
        return self.traces.get_tracer(name)
    
    def start_span(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> Span:
        """
        Start a new trace span.
        
        Args:
            name: Name of the span
            attributes: Attributes to add to the span
            
        Returns:
            A new span
        """
        return self.traces.start_span(name, attributes=attributes)
    
    @contextmanager
    def span(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> ContextManager[Span]:
        """
        Context manager for creating a span.
        
        Args:
            name: Name of the span
            attributes: Attributes to add to the span
            
        Returns:
            A context manager that yields a span
        """
        span = self.start_span(name, attributes)
        try:
            yield span
        except Exception as e:
            span.set_status(StatusCode.ERROR)
            span.record_exception(e)
            raise
        finally:
            span.end()
    
    def trace_function(self, name: Optional[str] = None, 
                      attributes: Optional[Dict[str, Any]] = None) -> Callable[[F], F]:
        """
        Decorator to trace a function.
        
        Args:
            name: Name for the span, defaults to function name
            attributes: Attributes to add to the span
            
        Returns:
            Decorator function
        """
        return self.traces.trace_function(name, attributes)
    
    def trace_data_processing(self, name: Optional[str] = None,
                             attributes: Optional[Dict[str, Any]] = None) -> Callable[[F], F]:
        """
        Decorator specialized for data processing functions.
        
        Args:
            name: Name for the span, defaults to function name with prefix
            attributes: Attributes to add to the span
            
        Returns:
            Decorator function
        """
        return self.traces.trace_data_processing(name, attributes)
    
    def data_operation(self, operation_type: str, target: Optional[str] = None,
                     attributes: Optional[Dict[str, Any]] = None) -> ContextManager[Span]:
        """
        Context manager for a standardized data operation.
        
        Args:
            operation_type: Type of operation (load, save, transform, etc.)
            target: Target of the operation (table name, file name, etc.)
            attributes: Additional attributes
            
        Returns:
            A context manager that yields a span
        """
        # Map to standard operation name if possible
        if operation_type in [
            "load", "save", "transform", "validate", "clean", 
            "filter", "aggregate", "join", "export"
        ]:
            span_name = format_span_name(f"data.{operation_type}", target)
        else:
            span_name = format_span_name("data.process", target or operation_type)
            
        # Always include the operation type in attributes
        all_attributes = {AttributeNames.DATA_OPERATION: operation_type}
        if target:
            all_attributes[AttributeNames.DATA_SOURCE] = target
            
        # Add user attributes
        if attributes:
            all_attributes.update(attributes)
            
        return self.span(span_name, all_attributes)
    
    #
    # Metrics API
    #
    
    def create_counter(self, name: str, description: str, unit: str = "1",
                      attributes: Optional[Dict[str, str]] = None) -> Any:
        """
        Create a counter metric.
        
        Args:
            name: Name of the counter
            description: Description of what the counter measures
            unit: Unit of measurement
            attributes: Default attributes to attach to all measurements
            
        Returns:
            A counter instrument
        """
        return self.metrics.create_counter(name, description, unit, attributes)
    
    def create_gauge(self, name: str, description: str, unit: str = "1",
                    attributes: Optional[Dict[str, str]] = None) -> Any:
        """
        Create a gauge metric.
        
        Args:
            name: Name of the gauge
            description: Description of what the gauge measures
            unit: Unit of measurement
            attributes: Default attributes to attach to all measurements
            
        Returns:
            A gauge instrument
        """
        return self.metrics.create_gauge(name, description, unit, attributes)
    
    def create_histogram(self, name: str, description: str, unit: str = "1",
                        attributes: Optional[Dict[str, str]] = None) -> Any:
        """
        Create a histogram metric.
        
        Args:
            name: Name of the histogram
            description: Description of what the histogram measures
            unit: Unit of measurement
            attributes: Default attributes to attach to all measurements
            
        Returns:
            A histogram instrument
        """
        return self.metrics.create_histogram(name, description, unit, attributes)
    
    def create_data_processing_metrics(self, prefix: str = "data") -> Dict[str, Any]:
        """
        Create a set of common metrics used in data processing scripts.
        
        Args:
            prefix: Prefix for all metric names
            
        Returns:
            Dictionary of metrics
        """
        return self.metrics.create_data_processing_metrics(prefix)
    
    #
    # Logging API
    #
    
    def get_logger(self, name: Optional[str] = None) -> DataLogger:
        """
        Get a logger instance.
        
        Args:
            name: Name for the logger, defaults to service name
            
        Returns:
            A configured logger
        """
        return self.logs.get_logger(name)
    
    #
    # Lifecycle API
    #
    
    def shutdown(self) -> None:
        """
        Shutdown all telemetry components properly.
        
        This ensures all buffered telemetry is flushed before the application exits.
        """
        try:
            self.traces.shutdown()
            self.metrics.shutdown()
            self.logs.shutdown()
            logger.info("Observability shutdown complete")
        except Exception as e:
            # Don't raise an exception during shutdown
            print(f"Error during observability shutdown: {str(e)}")
    
    #
    # Convenience methods
    #
    
    @contextmanager
    def timed_span(self, name: str, attributes: Optional[Dict[str, Any]] = None, 
                  histogram: Optional[Any] = None) -> ContextManager[Span]:
        """
        Context manager that creates a span and optionally records its duration in a histogram.
        
        Args:
            name: Name of the span
            attributes: Attributes to add to the span
            histogram: Optional histogram to record the duration
            
        Returns:
            A context manager that yields a span
        """
        start_time = time.time()
        with self.span(name, attributes) as span:
            try:
                yield span
            finally:
                if histogram:
                    duration = time.time() - start_time
                    histogram.record(duration, attributes)
    
    @contextmanager
    def timed_task(self, task_name: str, attributes: Optional[Dict[str, Any]] = None) -> ContextManager[Dict[str, Any]]:
        """
        High-level context manager for timing a task with metrics and traces.
        
        This creates a span and records standard metrics for the task.
        
        Args:
            task_name: Name of the task
            attributes: Attributes to add to telemetry
            
        Returns:
            A context manager that yields a context dict with span and metrics
        """
        metrics = {
            "duration": self.create_histogram(
                name=f"{task_name}_duration_seconds",
                description=f"Duration of {task_name} task in seconds",
                unit=MetricNames.Units.SECONDS
            ),
            "success": self.create_counter(
                name=f"{task_name}_success_total",
                description=f"Number of successful {task_name} tasks",
                unit=MetricNames.Units.COUNT
            ),
            "failure": self.create_counter(
                name=f"{task_name}_failure_total",
                description=f"Number of failed {task_name} tasks",
                unit=MetricNames.Units.COUNT
            )
        }
        
        start_time = time.time()
        with self.span(task_name, attributes) as span:
            context = {
                "span": span,
                "metrics": metrics,
                "attributes": attributes or {}
            }
            
            try:
                yield context
                duration = time.time() - start_time
                metrics["duration"].record(duration, attributes)
                metrics["success"].add(1, attributes)
            except Exception as e:
                duration = time.time() - start_time
                metrics["duration"].record(duration, attributes)
                metrics["failure"].add(1, attributes)
                # Re-raise the exception
                raise 