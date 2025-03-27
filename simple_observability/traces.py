"""Traces module for the observability library."""

import logging
import functools
import time
from typing import Optional, Dict, Any, List, Callable, TypeVar, cast

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter
)
from opentelemetry.trace import Span, Tracer, StatusCode

from .config import ObservabilityConfig
from .standards import AttributeNames, SpanNames, format_span_name, DATA_OPERATION_ATTRIBUTES

# Set up module logger
logger = logging.getLogger(__name__)

# Type variable for decorators
F = TypeVar('F', bound=Callable[..., Any])


class TraceManager:
    """
    Manager for trace instrumentation and exporting.
    
    This class handles the setup of OpenTelemetry traces, including
    exporters for console output and OTLP.
    """
    
    def __init__(self, config: ObservabilityConfig):
        """
        Initialize the trace manager with the provided configuration.
        
        Args:
            config: The observability configuration
        """
        self.config = config
        self.tracer_provider = None
        self._setup_traces()
        
    def _setup_traces(self):
        """Set up the tracing infrastructure."""
        try:
            # Create tracer provider
            self.tracer_provider = TracerProvider(
                resource=self.config.resource
            )
            
            # Add console exporter for development
            if self.config.enable_console_export:
                console_processor = BatchSpanProcessor(ConsoleSpanExporter())
                self.tracer_provider.add_span_processor(console_processor)
                logger.info("Enabled console span exporter")
                
            # Set up OTLP exporter if configured
            if self.config.otlp_endpoint:
                try:
                    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
                    otlp_exporter = OTLPSpanExporter(endpoint=self.config.otlp_endpoint)
                    otlp_processor = BatchSpanProcessor(otlp_exporter)
                    self.tracer_provider.add_span_processor(otlp_processor)
                    logger.info(f"Enabled OTLP span exporter to {self.config.otlp_endpoint}")
                except ImportError:
                    logger.warning("OTLP exporter requested but dependencies not installed")
                
            # Set as global tracer provider
            trace.set_tracer_provider(self.tracer_provider)
            logger.info(f"Traces initialized for service {self.config.service_name}")
            
        except Exception as e:
            logger.exception(f"Failed to set up traces: {str(e)}")
            # Set up a no-op tracer provider
            self.tracer_provider = TracerProvider(resource=self.config.resource)
            trace.set_tracer_provider(self.tracer_provider)
        
    def get_tracer(self, name: Optional[str] = None) -> Tracer:
        """
        Get a tracer for the given name.
        
        Args:
            name: Name of the tracer, defaults to service name
            
        Returns:
            A tracer instance
        """
        tracer_name = name or self.config.service_name
        return trace.get_tracer(tracer_name, self.config.service_version)
        
    def start_span(self, name: str, context: Optional[Any] = None, 
                  attributes: Optional[Dict[str, Any]] = None) -> Span:
        """
        Start a new span with the given name.
        
        Args:
            name: Name of the span (will be standardized if it matches a known operation)
            context: Context to use, defaults to current context
            attributes: Attributes to add to the span
            
        Returns:
            A new span
        """
        try:
            tracer = self.get_tracer()

            # Add standard attributes
            standard_attributes = {
                AttributeNames.SERVICE_NAME: self.config.service_name,
                AttributeNames.SERVICE_VERSION: self.config.service_version,
                AttributeNames.ENVIRONMENT: self.config.environment,
            }
            
            # Combine with user-provided attributes
            all_attributes = standard_attributes.copy()
            if attributes:
                all_attributes.update(attributes)
                
            # Use current context if none provided
            span = tracer.start_span(name)
            
            # Add all attributes
            for key, value in all_attributes.items():
                span.set_attribute(key, value)
                    
            return span
        except Exception as e:
            logger.exception(f"Failed to start span {name}: {str(e)}")
            # Return a no-op span
            return trace.INVALID_SPAN
    
    def trace_function(self, name: Optional[str] = None, 
                      attributes: Optional[Dict[str, Any]] = None) -> Callable[[F], F]:
        """
        Decorator to trace a function.
        
        Args:
            name: Name of the span, defaults to function name
            attributes: Attributes to add to the span
            
        Returns:
            Decorator function
        """
        def decorator(func: F) -> F:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                span_name = name or func.__name__
                span_attributes = attributes or {}
                
                # Add function name attribute
                span_attributes[AttributeNames.FUNCTION_NAME] = func.__name__
                
                with self.start_span(span_name, attributes=span_attributes) as span:
                    try:
                        start_time = time.time()
                        result = func(*args, **kwargs)
                        end_time = time.time()
                        duration = end_time - start_time
                        
                        span.set_attribute(AttributeNames.FUNCTION_DURATION, duration)
                        return result
                    except Exception as e:
                        span.set_status(StatusCode.ERROR)
                        span.record_exception(e)
                        span.set_attribute(AttributeNames.ERROR_TYPE, e.__class__.__name__)
                        span.set_attribute(AttributeNames.ERROR_MESSAGE, str(e))
                        raise
                        
            return cast(F, wrapper)
        return decorator
    
    def trace_data_processing(self, name: Optional[str] = None,
                             attributes: Optional[Dict[str, Any]] = None) -> Callable[[F], F]:
        """
        Decorator specialized for data processing functions.
        
        Adds additional attributes relevant to data operations.
        
        Args:
            name: Name of the span, defaults to function name
            attributes: Attributes to add to the span
            
        Returns:
            Decorator function
        """
        def decorator(func: F) -> F:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                # Use standard span naming for data operations
                operation_type = name or func.__name__
                
                # Try to map to a standard data operation name
                if operation_type.startswith("load") or operation_type.startswith("read"):
                    span_name = SpanNames.DATA_LOAD
                elif operation_type.startswith("save") or operation_type.startswith("write"):
                    span_name = SpanNames.DATA_SAVE
                elif operation_type.startswith("transform"):
                    span_name = SpanNames.DATA_TRANSFORM
                elif operation_type.startswith("clean"):
                    span_name = SpanNames.DATA_CLEAN
                elif operation_type.startswith("validate"):
                    span_name = SpanNames.DATA_VALIDATE
                elif operation_type.startswith("filter"):
                    span_name = SpanNames.DATA_FILTER
                elif operation_type.startswith("aggregate"):
                    span_name = SpanNames.DATA_AGGREGATE
                elif operation_type.startswith("join"):
                    span_name = SpanNames.DATA_JOIN
                elif operation_type.startswith("export"):
                    span_name = SpanNames.DATA_EXPORT
                else:
                    # Use format_span_name to apply standard formatting
                    span_name = format_span_name("data.process", func.__name__)
                
                # Add standard data operation attributes
                span_attributes = {AttributeNames.DATA_OPERATION: operation_type}
                if attributes:
                    span_attributes.update(attributes)
                
                # Try to extract data size if args[0] is a data object
                if args and hasattr(args[0], "__len__"):
                    try:
                        data_size = len(args[0])
                        span_attributes[AttributeNames.DATA_SIZE] = data_size
                    except (TypeError, AttributeError):
                        pass
                
                # Try to extract DataFrame information if pandas is used
                if args and hasattr(args[0], "shape"):
                    try:
                        shape = args[0].shape
                        if len(shape) == 2:  # DataFrame or numpy array
                            span_attributes[AttributeNames.DATA_ROWS] = shape[0]
                            span_attributes[AttributeNames.DATA_COLUMNS] = shape[1]
                    except (TypeError, AttributeError, IndexError):
                        pass
                
                with self.start_span(span_name, attributes=span_attributes) as span:
                    try:
                        start_time = time.time()
                        result = func(*args, **kwargs)
                        end_time = time.time()
                        duration = end_time - start_time
                        
                        span.set_attribute(AttributeNames.FUNCTION_DURATION, duration)
                        
                        # Try to extract result size
                        if result and hasattr(result, "__len__"):
                            try:
                                result_size = len(result)
                                span.set_attribute("data.result_size", result_size)
                            except (TypeError, AttributeError):
                                pass
                                
                        # Try to extract DataFrame result information
                        if result and hasattr(result, "shape"):
                            try:
                                shape = result.shape
                                if len(shape) == 2:  # DataFrame or numpy array
                                    span.set_attribute("data.result_rows", shape[0])
                                    span.set_attribute("data.result_columns", shape[1])
                            except (TypeError, AttributeError, IndexError):
                                pass
                                
                        return result
                    except Exception as e:
                        span.set_status(StatusCode.ERROR)
                        span.record_exception(e)
                        span.set_attribute(AttributeNames.ERROR_TYPE, e.__class__.__name__)
                        span.set_attribute(AttributeNames.ERROR_MESSAGE, str(e))
                        raise
                        
            return cast(F, wrapper)
        return decorator
        
    def shutdown(self):
        """Shutdown trace exporters."""
        if self.tracer_provider:
            self.tracer_provider.shutdown()
            logger.info("Traces infrastructure shut down") 