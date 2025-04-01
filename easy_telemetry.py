#!/usr/bin/env python3
"""
Easy Telemetry - Simple OpenTelemetry wrapper
--------------------------------------------

A library that simplifies the configuration and use of OpenTelemetry
for Python applications.
"""

# Standard library imports
import logging
import sys
import time
import json
from typing import Dict, Any, Optional, List

# OpenTelemetry core imports
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION, DEPLOYMENT_ENVIRONMENT

# Tracing imports
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

# Metrics imports
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader

# Logging imports
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.trace import format_trace_id, format_span_id




class Telemetry:
    """
    Main class that configures and exposes OpenTelemetry functionality.
    
    This class provides an easy way to set up tracing, metrics, and logging
    with sensible defaults.
    """
    
    def __init__(
        self,
        service_name: str,
        service_version: str = "0.1.0",
        environment: str = "development",
        resource_attributes: Optional[Dict[str, str]] = None,
        log_level: int = logging.INFO,
        use_json_logs: bool = False
    ):
        """
        Initialize the OpenTelemetry wrapper with configuration for the service.
        
        Args:
            service_name: Name of the service (required)
            service_version: Version of the service
            environment: Deployment environment (development, staging, production)
            resource_attributes: Additional resource attributes
            log_level: Minimum log level to capture
            use_json_logs: Whether to output logs in JSON format
        """
        # Store basic service information
        self.service_name = service_name
        self.service_version = service_version
        self.environment = environment
        self.log_level = log_level
        self.use_json_logs = use_json_logs
        
        # Create resource attributes dictionary
        resource_attrs = {
            SERVICE_NAME: service_name,
            SERVICE_VERSION: service_version,
            DEPLOYMENT_ENVIRONMENT: environment,
        }
        
        # Add any additional resource attributes
        if resource_attributes:
            resource_attrs.update(resource_attributes)
            
        # Create the OpenTelemetry resource
        self.resource = Resource.create(resource_attrs)
        
        # Component references (will be set up later)
        self.tracer = None
        self.meter = None
        self.logger = None
        
        # Set up tracing
        self._setup_tracing()
        
        # Set up metrics
        self._setup_metrics()
        
        # Set up logging (after tracing is configured)
        self._setup_logging()
        
    def _setup_tracing(self):
        """
        Configure OpenTelemetry tracing.
        
        This sets up:
        1. A tracer provider with our service resource
        2. A console exporter to output spans to stdout
        3. A batch processor to efficiently export spans
        """
        # Create a tracer provider with our resource
        tracer_provider = TracerProvider(resource=self.resource)
        
        # Create a console exporter
        # This sends span data to stdout (useful for development)
        console_exporter = ConsoleSpanExporter()
        
        # Create a batch span processor
        # This collects spans and exports them in batches for efficiency
        span_processor = BatchSpanProcessor(console_exporter)
        
        # Add the processor to the provider
        # Any traces created will flow through the processor to the exporter.
        tracer_provider.add_span_processor(span_processor)
        
        # Set this provider as the global default (setup the standard)
        trace.set_tracer_provider(tracer_provider)
        
        # Store provider reference for later use 
        self.tracer_provider = tracer_provider
        
        # Create a tracer for this service
        self.tracer = trace.get_tracer(
            self.service_name,
            self.service_version
        )
        
    def _setup_metrics(self):
        """
        Configure OpenTelemetry metrics.
        
        This sets up:
        1. A meter provider with our service resource
        2. A console exporter to output metrics to stdout
        3. A periodic metric reader to export metrics at regular intervals
        """
        # Create a console exporter for metrics
        # This sends metrics data to stdout (useful for development)
        console_exporter = ConsoleMetricExporter()
        
        # Create a metric reader that exports metrics every 30 seconds
        reader = PeriodicExportingMetricReader(
            console_exporter,
            export_interval_millis=30000 
        )
        
        # Create a meter provider with our resource
        meter_provider = MeterProvider(
            resource=self.resource,
            metric_readers=[reader]
        )
        
        # Set this provider as the global default
        metrics.set_meter_provider(meter_provider)
        
        # Store provider reference for later use
        self.meter_provider = meter_provider
        
        # Create a meter for this service
        self.meter = metrics.get_meter(
            self.service_name,
            self.service_version
        )
        
    def _setup_logging(self):
        """
        Configure logging with trace context.
        
        This sets up:
        1. A formatter that adds trace context to log messages
        2. A handler that sends logs to stdout
        3. A logger for this service
        """
        # Create the appropriate formatter based on configuration
        if self.use_json_logs:
            formatter = JsonLogFormatter()
        else:
            formatter = TraceContextFormatter(
                fmt='%(asctime)s [%(levelname)s] %(name)s - trace_id=%(trace_id)s span_id=%(span_id)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        # Create a handler that sends logs to stdout
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        
        # Configure the root logger
        root_logger = logging.getLogger()
        root_logger.handlers = [handler]  # Replace any existing handlers
        root_logger.setLevel(self.log_level)
        
        # Create a logger for this service
        self.logger = logging.getLogger(self.service_name)
        
        # Log an initialization message
        self.logger.info(f"Telemetry initialized for service: {self.service_name}")

        
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """
        Get a logger with the specified name.
        
        The logger will include trace context in its outputs.
        
        Args:
            name: Name for the logger (default: use service name)
            
        Returns:
            A configured logger
        """
        logger_name = name if name else self.service_name
        return logging.getLogger(logger_name)
        
    def get_tracer(self, name: Optional[str] = None) -> trace.Tracer:
        """
        Get a tracer with the specified name.
        
        Args:
            name: Name for the tracer (default: use service name)
            
        Returns:
            An OpenTelemetry tracer
        """
        tracer_name = name if name else self.service_name
        return trace.get_tracer(tracer_name, self.service_version)
        
    def get_meter(self, name: Optional[str] = None) -> metrics.Meter:
        """
        Get a meter with the specified name.
        
        Args:
            name: Name for the meter (default: use service name)
            
        Returns:
            An OpenTelemetry meter
        """
        meter_name = name if name else self.service_name
        return metrics.get_meter(meter_name, self.service_version)


class TraceContextFormatter(logging.Formatter):
    """
    Custom formatter that adds trace context to log messages.
    
    This formatter adds the current trace_id and span_id to each log message,
    allowing logs to be correlated with traces.
    """
    
    def format(self, record):
        """Add trace context to the log record before formatting."""
        # Get the current span from the context
        span = trace.get_current_span()
        span_context = span.get_span_context()
        
        # Add trace and span IDs to the record if a span is active
        if span_context.is_valid:
            record.trace_id = format_trace_id(span_context.trace_id)
            record.span_id = format_span_id(span_context.span_id)
        else:
            # No active span, use placeholder values
            record.trace_id = "00000000000000000000000000000000"
            record.span_id = "0000000000000000"
            
        # Call the parent formatter
        return super().format(record)


class JsonLogFormatter(logging.Formatter):
    """
    Formatter that outputs logs as JSON with trace context.
    
    This is useful for sending logs to systems that can parse JSON.
    """
    
    def format(self, record):
        """Format the log record as JSON with trace context."""
        # Create a dictionary with the basic log information
        log_data = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        # Get the current span from the context
        span = trace.get_current_span()
        span_context = span.get_span_context()
        
        # Add trace and span IDs if a span is active
        if span_context.is_valid:
            log_data["trace_id"] = format_trace_id(span_context.trace_id)
            log_data["span_id"] = format_span_id(span_context.span_id)
            
        # Convert to JSON string
        return json.dumps(log_data)
