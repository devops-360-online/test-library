"""Configuration module for the observability library."""

from dataclasses import dataclass, field
import logging
import os
from typing import Optional, Dict, Any, List

from opentelemetry.sdk.resources import Resource

from .standards import LogFormat, Environment


@dataclass
class ObservabilityConfig:
    """Configuration for all observability components.
    
    This class centralizes all configuration options for metrics, logs, and traces
    to ensure consistent setup across all telemetry types.
    """
    # Basic service information
    service_name: str
    service_version: str = "0.1.0"
    environment: str = Environment.DEVELOPMENT.value
    
    # Exporter configurations
    prometheus_port: int = 8000
    otlp_endpoint: Optional[str] = None
    enable_console_export: bool = True
    
    # Logging configuration
    log_level: int = logging.INFO
    log_format: str = LogFormat.BASIC
    json_logs: bool = False  # Whether to use JSON format for logs
    
    # Additional attributes
    additional_attributes: Dict[str, Any] = field(default_factory=dict)
    
    # Internal use
    resource: Optional[Resource] = None
    
    @classmethod
    def from_env(cls, service_name: str) -> 'ObservabilityConfig':
        """
        Create a configuration from environment variables.
        
        Args:
            service_name: The name of the service
            
        Returns:
            A configuration object with settings from environment variables
        """
        # Get environment variables with defaults
        service_version = os.environ.get('SERVICE_VERSION', '0.1.0')
        environment = os.environ.get('ENVIRONMENT', Environment.DEVELOPMENT.value)
        prometheus_port = int(os.environ.get('PROMETHEUS_PORT', '8000'))
        otlp_endpoint = os.environ.get('OTLP_ENDPOINT')
        log_level_name = os.environ.get('LOG_LEVEL', 'INFO')
        log_level = getattr(logging, log_level_name, logging.INFO)
        enable_console = os.environ.get('ENABLE_CONSOLE_EXPORT', 'true').lower() in ('true', '1', 'yes')
        json_logs = os.environ.get('JSON_LOGS', 'false').lower() in ('true', '1', 'yes')
        
        # In production, enable JSON logs by default
        if environment.lower() == Environment.PRODUCTION.value.lower() and 'JSON_LOGS' not in os.environ:
            json_logs = True
            
        # Create the configuration
        return cls(
            service_name=service_name,
            service_version=service_version,
            environment=environment,
            prometheus_port=prometheus_port,
            otlp_endpoint=otlp_endpoint,
            enable_console_export=enable_console,
            log_level=log_level,
            log_format=LogFormat.TRACE_CONTEXT,
            json_logs=json_logs,
        )
        
    def __post_init__(self):
        """Initialize resource after initialization."""
        attributes = {
            "service.name": self.service_name,
            "service.version": self.service_version,
            "deployment.environment": self.environment,
        }
        
        # Add any additional attributes
        attributes.update(self.additional_attributes)
        
        # Create the resource
        self.resource = Resource.create(attributes) 