"""
Standards for observability components.

This module defines standardized formats, naming conventions, and labels for
logs, metrics, and traces to ensure consistency across all applications.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
import re

# -----------------------------------------------------------------------------
# Common standards
# -----------------------------------------------------------------------------

class Environment(Enum):
    """Standard environment names."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


# Standard attribute names to use consistently across all telemetry
class AttributeNames:
    """Standard attribute names for telemetry data."""
    # Common attributes
    SERVICE_NAME = "service.name"
    SERVICE_VERSION = "service.version"
    ENVIRONMENT = "deployment.environment"
    HOST_NAME = "host.name"
    
    # Error attributes
    ERROR_TYPE = "error.type"
    ERROR_MESSAGE = "error.message"
    ERROR_STACK = "error.stack_trace"
    
    # Data processing attributes
    DATA_SOURCE = "data.source"
    DATA_FORMAT = "data.format"
    DATA_SIZE = "data.size"
    DATA_ROWS = "data.rows"
    DATA_COLUMNS = "data.columns"
    DATA_OPERATION = "data.operation"
    DATA_DESTINATION = "data.destination"
    
    # Function attributes
    FUNCTION_NAME = "function.name"
    FUNCTION_DURATION = "function.duration_seconds"
    
    # Batch processing
    BATCH_ID = "batch.id"
    BATCH_SIZE = "batch.size"
    
    # File processing
    FILE_NAME = "file.name"
    FILE_SIZE = "file.size_bytes"
    FILE_PATH = "file.path"
    FILE_TYPE = "file.type"


# -----------------------------------------------------------------------------
# Metric standards
# -----------------------------------------------------------------------------

class MetricNames:
    """Standard metric names for data applications."""
    
    # Base prefixes
    DATA_PREFIX = "data_"
    FILE_PREFIX = "file_"
    DATABASE_PREFIX = "db_"
    API_PREFIX = "api_"
    MEMORY_PREFIX = "memory_"
    PROCESSING_PREFIX = "processing_"
    
    # Counter metrics
    ROWS_PROCESSED = "rows_processed_total"
    ROWS_FILTERED = "rows_filtered_total"
    ERRORS_TOTAL = "errors_total"
    PROCESSING_TIME = "processing_seconds"
    MEMORY_USAGE = "memory_bytes"
    BATCH_SIZE = "batch_size"
    
    # Standard units for metrics
    class Units:
        """Standard units for metrics."""
        SECONDS = "s"
        MILLISECONDS = "ms"
        BYTES = "By"
        ROWS = "rows"
        COUNT = "1"  # Dimensionless


def standardize_metric_name(name: str, prefix: Optional[str] = None) -> str:
    """
    Standardize a metric name to follow conventions.
    
    Args:
        name: The base metric name
        prefix: Optional prefix to add
        
    Returns:
        A standardized metric name
    """
    # Convert camelCase or PascalCase to snake_case
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    snake_case = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    # Add prefix if provided
    if prefix:
        if not prefix.endswith('_'):
            prefix = f"{prefix}_"
        return f"{prefix}{snake_case}"
    
    return snake_case


def get_standard_data_metrics(prefix: str) -> Dict[str, Dict[str, str]]:
    """
    Get standard metric definitions for data processing.
    
    Args:
        prefix: Prefix for the metrics
        
    Returns:
        Dictionary of metric definitions with name, description, and unit
    """
    return {
        "rows_processed": {
            "name": f"{prefix}_{MetricNames.ROWS_PROCESSED}",
            "description": "Total number of data rows processed",
            "unit": MetricNames.Units.ROWS
        },
        "processing_errors": {
            "name": f"{prefix}_errors_total",
            "description": "Total number of errors during data processing",
            "unit": MetricNames.Units.COUNT
        },
        "processing_duration": {
            "name": f"{prefix}_processing_duration_seconds",
            "description": "Time taken to process data",
            "unit": MetricNames.Units.SECONDS
        },
        "batch_size": {
            "name": f"{prefix}_{MetricNames.BATCH_SIZE}",
            "description": "Size of data batches processed",
            "unit": MetricNames.Units.ROWS
        },
        "memory_usage": {
            "name": f"{prefix}_memory_usage_bytes",
            "description": "Memory usage during data processing",
            "unit": MetricNames.Units.BYTES
        }
    }


# -----------------------------------------------------------------------------
# Log standards
# -----------------------------------------------------------------------------

class LogLevel(Enum):
    """Standard log levels mapped to Python logging levels."""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class LogFormat:
    """Standard log formats."""
    
    # Basic format with timestamp, level, and message
    BASIC = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    
    # JSON format for structured logging
    JSON = {
        "timestamp": "%(asctime)s",
        "level": "%(levelname)s",
        "logger": "%(name)s",
        "message": "%(message)s",
        "module": "%(module)s",
        "function": "%(funcName)s",
        "line": "%(lineno)d"
    }
    
    # Format with trace context
    TRACE_CONTEXT = "%(asctime)s [%(levelname)s] [trace_id=%(trace_id)s span_id=%(span_id)s] %(name)s: %(message)s"


# Standard fields that should be included in all structured logs
STANDARD_LOG_FIELDS = [
    "timestamp",
    "level",
    "message",
    "service",
    "trace_id",  # From trace context
    "span_id",   # From trace context
]


# -----------------------------------------------------------------------------
# Trace standards
# -----------------------------------------------------------------------------

class SpanNames:
    """Standard span names for common operations."""
    
    # Data operations
    DATA_LOAD = "data.load"
    DATA_SAVE = "data.save"
    DATA_TRANSFORM = "data.transform"
    DATA_VALIDATE = "data.validate"
    DATA_CLEAN = "data.clean"
    DATA_FILTER = "data.filter"
    DATA_AGGREGATE = "data.aggregate"
    DATA_JOIN = "data.join"
    DATA_EXPORT = "data.export"
    
    # Database operations
    DB_QUERY = "db.query"
    DB_INSERT = "db.insert"
    DB_UPDATE = "db.update"
    DB_DELETE = "db.delete"
    
    # File operations
    FILE_READ = "file.read"
    FILE_WRITE = "file.write"
    
    # API operations
    API_REQUEST = "api.request"
    API_RESPONSE = "api.response"


def format_span_name(operation: str, target: Optional[str] = None) -> str:
    """
    Format a span name according to standards.
    
    Args:
        operation: The operation being performed
        target: Optional target of the operation (e.g., table name, file name)
        
    Returns:
        Formatted span name
    """
    if target:
        return f"{operation}.{target}"
    return operation


# Standard span attributes that should be captured for data operations
DATA_OPERATION_ATTRIBUTES = [
    AttributeNames.DATA_OPERATION,
    AttributeNames.DATA_SOURCE,
    AttributeNames.DATA_SIZE,
    AttributeNames.FUNCTION_DURATION,
] 