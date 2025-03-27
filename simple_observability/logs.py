"""Logging module for the observability library."""

import logging
import sys
import threading
import json
from typing import Optional, Dict, Any, List

from opentelemetry.sdk._logs import LoggerProvider, LogRecord, SeverityNumber
from opentelemetry.sdk._logs.export import (
    BatchLogRecordProcessor,
    ConsoleLogExporter
)
from opentelemetry._logs import get_logger, Logger, set_logger_provider

from .config import ObservabilityConfig
from .standards import LogFormat, LogLevel, STANDARD_LOG_FIELDS, AttributeNames

# Set up module logger
logger = logging.getLogger(__name__)

# Thread-local storage for current span context
_thread_local = threading.local()


class SpanContextHandler(logging.Handler):
    """Handler that attaches current span context to logs."""
    
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)
        
    def emit(self, record):
        try:
            from opentelemetry import trace
            
            # Get current span
            current_span = trace.get_current_span()
            
            # Attach span info to record if span is valid
            if current_span and current_span.is_recording():
                span_context = current_span.get_span_context()
                if span_context.is_valid:
                    record.trace_id = format(span_context.trace_id, '032x')
                    record.span_id = format(span_context.span_id, '016x')
        except Exception:
            # Just continue if there's an issue with span context
            pass


class OpenTelemetryLogHandler(logging.Handler):
    """Handler that converts standard Python logs to OpenTelemetry log records."""
    
    def __init__(self, otel_logger: Logger, service_name: str, service_version: str, environment: str):
        super().__init__()
        self.otel_logger = otel_logger
        self.service_name = service_name
        self.service_version = service_version
        self.environment = environment
        
    def emit(self, record: logging.LogRecord):
        try:
            msg = self.format(record)
            
            # Standard attributes that should be included in all logs
            attributes = {
                AttributeNames.SERVICE_NAME: self.service_name,
                AttributeNames.SERVICE_VERSION: self.service_version,
                AttributeNames.ENVIRONMENT: self.environment,
                "log.function": record.funcName,
                "log.file.name": record.filename,
                "log.line": record.lineno,
                "log.logger": record.name,
            }
            
            # Add trace context if available
            if hasattr(record, 'trace_id'):
                attributes["trace_id"] = record.trace_id
            if hasattr(record, 'span_id'):
                attributes["span_id"] = record.span_id
            
            # Map severity level using our standard mapping
            severity = {
                LogLevel.DEBUG.value: SeverityNumber.DEBUG,
                LogLevel.INFO.value: SeverityNumber.INFO,
                LogLevel.WARNING.value: SeverityNumber.WARN,
                LogLevel.ERROR.value: SeverityNumber.ERROR,
                LogLevel.CRITICAL.value: SeverityNumber.FATAL
            }.get(record.levelno, SeverityNumber.INFO)
            
            # Add attributes from record
            if hasattr(record, 'data') and isinstance(record.data, dict):
                attributes.update(record.data)
            
            # If exception info is available, add it to attributes
            if record.exc_info:
                exc_type, exc_value, exc_tb = record.exc_info
                attributes[AttributeNames.ERROR_TYPE] = exc_type.__name__
                attributes[AttributeNames.ERROR_MESSAGE] = str(exc_value)
            
            # Create and emit OpenTelemetry log record
            self.otel_logger.emit(
                severity=severity,
                body=msg,
                attributes=attributes
            )
        except Exception:
            self.handleError(record)


class StructuredLogFormatter(logging.Formatter):
    """Formatter that creates structured logs with trace context."""
    
    def __init__(self, fmt=None, datefmt=None, style='%', use_json=False):
        super().__init__(fmt, datefmt, style)
        self.use_json = use_json
    
    def format(self, record):
        """Format log record into structured string or JSON."""
        # Start with standard formatting
        message = super().format(record)
        
        if self.use_json:
            # Create a JSON structure
            log_data = {
                "timestamp": self.formatTime(record, self.datefmt),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
            
            # Add trace context if available
            if hasattr(record, 'trace_id') and hasattr(record, 'span_id'):
                log_data["trace_id"] = record.trace_id
                log_data["span_id"] = record.span_id
                
            # Add extra attributes from record
            if hasattr(record, 'data') and isinstance(record.data, dict):
                for key, value in record.data.items():
                    log_data[key] = value
                    
            # Convert to JSON string
            return json.dumps(log_data)
        else:
            # Add trace context if available
            if hasattr(record, 'trace_id') and hasattr(record, 'span_id'):
                return f"{message} [trace_id={record.trace_id}, span_id={record.span_id}]"
            
            return message


class DataLogger(logging.Logger):
    """Extended logger class with methods for data-specific logging."""
    
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        
    def with_data(self, **kwargs):
        """
        Create a logging context with data attributes.
        
        Args:
            **kwargs: Data attributes to include in log records
            
        Returns:
            DataLoggingContext that can be used as a context manager
        """
        return DataLoggingContext(self, kwargs)
        
    def data(self, level, msg, *args, **kwargs):
        """
        Log with data attributes.
        
        Args:
            level: Log level
            msg: Log message
            *args: Format args for message
            **kwargs: Data attributes to include with the log
        """
        if not self.isEnabledFor(level):
            return
            
        data = kwargs.pop('data', {})
        extra = kwargs.pop('extra', {})
        extra['data'] = data
        
        self._log(level, msg, args, extra=extra, **kwargs)


class DataLoggingContext:
    """Context manager for logging with data attributes."""
    
    def __init__(self, logger, data):
        self.logger = logger
        self.data = data
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
        
    def debug(self, msg, *args, **kwargs):
        self._log(logging.DEBUG, msg, args, kwargs)
        
    def info(self, msg, *args, **kwargs):
        self._log(logging.INFO, msg, args, kwargs)
        
    def warning(self, msg, *args, **kwargs):
        self._log(logging.WARNING, msg, args, kwargs)
        
    def error(self, msg, *args, **kwargs):
        self._log(logging.ERROR, msg, args, kwargs)
        
    def critical(self, msg, *args, **kwargs):
        self._log(logging.CRITICAL, msg, args, kwargs)
        
    def _log(self, level, msg, args, kwargs):
        data = kwargs.pop('data', {})
        extra = kwargs.pop('extra', {})
        
        # Merge context data with call-specific data
        combined_data = self.data.copy()
        combined_data.update(data)
        extra['data'] = combined_data
        
        self.logger._log(level, msg, args, extra=extra, **kwargs)


# Register our custom logger class
logging.setLoggerClass(DataLogger)


class LogManager:
    """
    Manager for logging configuration and providing loggers.
    
    This class handles the setup of Python logging and integration with
    OpenTelemetry logs.
    """
    
    def __init__(self, config: ObservabilityConfig):
        """
        Initialize the log manager with the provided configuration.
        
        Args:
            config: The observability configuration
        """
        self.config = config
        self.logger_provider = None
        self.use_json = config.environment.lower() in ['production', 'staging']
        self._setup_logging()
        
    def _setup_logging(self):
        """Set up the logging infrastructure."""
        try:
            # Create logger provider
            self.logger_provider = LoggerProvider(
                resource=self.config.resource
            )
            
            # Add console exporter for development
            if self.config.enable_console_export:
                console_processor = BatchLogRecordProcessor(ConsoleLogExporter())
                self.logger_provider.add_log_record_processor(console_processor)
                logger.info("Enabled console log exporter")
                
            # Set up OTLP exporter if configured
            if self.config.otlp_endpoint:
                try:
                    from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
                    otlp_exporter = OTLPLogExporter(endpoint=self.config.otlp_endpoint)
                    otlp_processor = BatchLogRecordProcessor(otlp_exporter)
                    self.logger_provider.add_log_record_processor(otlp_processor)
                    logger.info(f"Enabled OTLP log exporter to {self.config.otlp_endpoint}")
                except ImportError:
                    logger.warning("OTLP exporter requested but dependencies not installed")
                
            # Set as global logger provider
            set_logger_provider(self.logger_provider)
            
            # Configure root Python logger
            root_logger = logging.getLogger()
            
            # Clear existing handlers to avoid duplicates
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
                
            # Set the level
            root_logger.setLevel(self.config.log_level)
            
            # Create console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.config.log_level)
            
            # Create formatter - select format based on environment
            if self.use_json:
                formatter = StructuredLogFormatter(
                    fmt=None,  # Not used for JSON
                    datefmt=None,  # Not used for JSON
                    use_json=True
                )
            else:
                formatter = StructuredLogFormatter(
                    fmt=LogFormat.TRACE_CONTEXT if self.config.enable_console_export else LogFormat.BASIC,
                    use_json=False
                )
                
            console_handler.setFormatter(formatter)
            
            # Add handlers
            root_logger.addHandler(console_handler)
            
            # Add span context handler
            span_handler = SpanContextHandler()
            span_handler.setLevel(logging.NOTSET)  # Process all records
            root_logger.addHandler(span_handler)
            
            # Add OpenTelemetry handler
            otel_logger = get_logger(
                self.config.service_name,
                logger_provider=self.logger_provider
            )
            otel_handler = OpenTelemetryLogHandler(
                otel_logger,
                self.config.service_name,
                self.config.service_version,
                self.config.environment
            )
            otel_handler.setFormatter(formatter)
            root_logger.addHandler(otel_handler)
            
            logger.info(f"Logging initialized for service {self.config.service_name}")
            
        except Exception as e:
            # If setup fails, ensure basic logging still works
            print(f"Failed to set up logging: {str(e)}")
            logging.basicConfig(
                level=self.config.log_level,
                format=LogFormat.BASIC,
                stream=sys.stdout
            )
        
    def get_logger(self, name: Optional[str] = None) -> DataLogger:
        """
        Get a logger with the given name.
        
        Args:
            name: Name of the logger, defaults to service name
            
        Returns:
            A configured logger
        """
        logger_name = name or self.config.service_name
        return logging.getLogger(logger_name)
        
    def shutdown(self):
        """Shutdown log exporters."""
        if self.logger_provider:
            self.logger_provider.shutdown()
            logger.info("Logging infrastructure shut down") 