"""Metrics module for the observability library."""

import logging
from typing import Optional, Dict, Any, List, Union, Callable

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader
)
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from prometheus_client import start_http_server

from .config import ObservabilityConfig
from .standards import MetricNames, get_standard_data_metrics, standardize_metric_name, AttributeNames

# Set up module logger
logger = logging.getLogger(__name__)


class MetricsManager:
    """
    Manager for metrics instrumentation and exporting.
    
    This class handles the setup of OpenTelemetry metrics, including
    exporters for Prometheus and OTLP.
    """
    
    def __init__(self, config: ObservabilityConfig):
        """
        Initialize the metrics manager with the provided configuration.
        
        Args:
            config: The observability configuration
        """
        self.config = config
        self.meter_provider = None
        self.meter = None
        self._setup_metrics()
        
    def _setup_metrics(self):
        """Set up the metrics infrastructure."""
        try:
            # Create metric readers
            readers = []
            
            # Add Prometheus exporter
            prometheus_reader = PrometheusMetricReader()
            readers.append(prometheus_reader)
            
            # Start Prometheus endpoint
            start_http_server(port=self.config.prometheus_port)
            logger.info(f"Started Prometheus metrics endpoint on port {self.config.prometheus_port}")
            
            # Add console exporter for development
            if self.config.enable_console_export:
                console_reader = PeriodicExportingMetricReader(
                    ConsoleMetricExporter(),
                    export_interval_millis=5000
                )
                readers.append(console_reader)
                logger.info("Enabled console metric exporter")
                
            # Set up OTLP exporter if configured
            if self.config.otlp_endpoint:
                try:
                    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
                    otlp_reader = PeriodicExportingMetricReader(
                        OTLPMetricExporter(endpoint=self.config.otlp_endpoint)
                    )
                    readers.append(otlp_reader)
                    logger.info(f"Enabled OTLP metric exporter to {self.config.otlp_endpoint}")
                except ImportError:
                    logger.warning("OTLP exporter requested but dependencies not installed")
                
            # Create and set meter provider
            self.meter_provider = MeterProvider(
                resource=self.config.resource,
                metric_readers=readers
            )
            metrics.set_meter_provider(self.meter_provider)
            
            # Create default meter
            self.meter = metrics.get_meter(
                self.config.service_name,
                version=self.config.service_version
            )
            logger.info(f"Metrics initialized for service {self.config.service_name}")
            
        except Exception as e:
            logger.exception(f"Failed to set up metrics: {str(e)}")
            # Create a no-op meter provider
            self.meter_provider = MeterProvider(resource=self.config.resource)
            metrics.set_meter_provider(self.meter_provider)
            self.meter = metrics.get_meter(self.config.service_name)
        
    def create_counter(self, name: str, description: str, unit: str = "1", 
                      attributes: Optional[Dict[str, str]] = None):
        """
        Create a counter metric.
        
        Args:
            name: Name of the counter (will be standardized)
            description: Description of what the counter measures
            unit: Unit of measurement
            attributes: Default attributes to attach to all measurements
            
        Returns:
            A counter instrument
        """
        try:
            # Apply naming standards
            std_name = standardize_metric_name(name)
            
            counter = self.meter.create_counter(
                name=std_name,
                description=description,
                unit=unit,
            )
            logger.debug(f"Created counter metric: {std_name}")
            
            # Standard attributes to always include
            standard_attrs = {
                AttributeNames.SERVICE_NAME: self.config.service_name,
                AttributeNames.SERVICE_VERSION: self.config.service_version,
                AttributeNames.ENVIRONMENT: self.config.environment
            }
            
            # Merge with provided attributes
            all_default_attrs = standard_attrs.copy()
            if attributes:
                all_default_attrs.update(attributes)
                
            # If attributes are provided, create a helper function to always include them
            if all_default_attrs:
                original_add = counter.add
                
                def add_with_default_attributes(value, additional_attributes=None):
                    all_attributes = all_default_attrs.copy()
                    if additional_attributes:
                        all_attributes.update(additional_attributes)
                    original_add(value, all_attributes)
                
                counter.add = add_with_default_attributes
                
            return counter
        except Exception as e:
            logger.exception(f"Failed to create counter metric {name}: {str(e)}")
            # Return a no-op counter
            return NoOpCounter(name)
        
    def create_gauge(self, name: str, description: str, unit: str = "1",
                    attributes: Optional[Dict[str, str]] = None):
        """
        Create a gauge metric (implemented as up-down counter in OpenTelemetry).
        
        Args:
            name: Name of the gauge (will be standardized)
            description: Description of what the gauge measures
            unit: Unit of measurement
            attributes: Default attributes to attach to all measurements
            
        Returns:
            A gauge instrument
        """
        try:
            # Apply naming standards
            std_name = standardize_metric_name(name)
            
            gauge = self.meter.create_up_down_counter(
                name=std_name,
                description=description,
                unit=unit,
            )
            logger.debug(f"Created gauge metric: {std_name}")
            
            # Standard attributes to always include
            standard_attrs = {
                AttributeNames.SERVICE_NAME: self.config.service_name,
                AttributeNames.SERVICE_VERSION: self.config.service_version,
                AttributeNames.ENVIRONMENT: self.config.environment
            }
            
            # Merge with provided attributes
            all_default_attrs = standard_attrs.copy()
            if attributes:
                all_default_attrs.update(attributes)
                
            # If attributes are provided, create a helper function to always include them
            if all_default_attrs:
                original_add = gauge.add
                
                def add_with_default_attributes(value, additional_attributes=None):
                    all_attributes = all_default_attrs.copy()
                    if additional_attributes:
                        all_attributes.update(additional_attributes)
                    original_add(value, all_attributes)
                
                gauge.add = add_with_default_attributes
                
            return gauge
        except Exception as e:
            logger.exception(f"Failed to create gauge metric {name}: {str(e)}")
            # Return a no-op gauge
            return NoOpCounter(name)
        
    def create_histogram(self, name: str, description: str, unit: str = "1",
                        attributes: Optional[Dict[str, str]] = None):
        """
        Create a histogram metric.
        
        Args:
            name: Name of the histogram (will be standardized)
            description: Description of what the histogram measures
            unit: Unit of measurement
            attributes: Default attributes to attach to all measurements
            
        Returns:
            A histogram instrument
        """
        try:
            # Apply naming standards
            std_name = standardize_metric_name(name)
            
            histogram = self.meter.create_histogram(
                name=std_name,
                description=description,
                unit=unit,
            )
            logger.debug(f"Created histogram metric: {std_name}")
            
            # Standard attributes to always include
            standard_attrs = {
                AttributeNames.SERVICE_NAME: self.config.service_name,
                AttributeNames.SERVICE_VERSION: self.config.service_version,
                AttributeNames.ENVIRONMENT: self.config.environment
            }
            
            # Merge with provided attributes
            all_default_attrs = standard_attrs.copy()
            if attributes:
                all_default_attrs.update(attributes)
                
            # If attributes are provided, create a helper function to always include them
            if all_default_attrs:
                original_record = histogram.record
                
                def record_with_default_attributes(value, additional_attributes=None):
                    all_attributes = all_default_attrs.copy()
                    if additional_attributes:
                        all_attributes.update(additional_attributes)
                    original_record(value, all_attributes)
                
                histogram.record = record_with_default_attributes
                
            return histogram
        except Exception as e:
            logger.exception(f"Failed to create histogram metric {name}: {str(e)}")
            # Return a no-op histogram
            return NoOpHistogram(name)
        
    def create_data_processing_metrics(self, prefix: str = "data"):
        """
        Create a set of common metrics used in data processing scripts.
        
        This is a convenience method to get standard metrics for data operations.
        
        Args:
            prefix: Prefix for all metric names
            
        Returns:
            Dictionary of metrics
        """
        # Get standard definitions
        metric_defs = get_standard_data_metrics(prefix)
        metrics_dict = {}
        
        # Create each metric
        for key, definition in metric_defs.items():
            if key in ["rows_processed", "processing_errors"]:
                metrics_dict[key] = self.create_counter(
                    name=definition["name"],
                    description=definition["description"],
                    unit=definition["unit"]
                )
            elif key in ["processing_duration", "batch_size"]:
                metrics_dict[key] = self.create_histogram(
                    name=definition["name"],
                    description=definition["description"],
                    unit=definition["unit"]
                )
            elif key in ["memory_usage"]:
                metrics_dict[key] = self.create_gauge(
                    name=definition["name"],
                    description=definition["description"],
                    unit=definition["unit"]
                )
                
        return metrics_dict
        
    def shutdown(self):
        """Shutdown metric exporters."""
        if self.meter_provider:
            self.meter_provider.shutdown()
            logger.info("Metrics infrastructure shut down")


# No-op implementations for error cases

class NoOpCounter:
    """No-op counter that does nothing but logs."""
    
    def __init__(self, name):
        self.name = name
        
    def add(self, value, attributes=None):
        logger.debug(f"No-op counter {self.name}.add({value}, {attributes})")


class NoOpHistogram:
    """No-op histogram that does nothing but logs."""
    
    def __init__(self, name):
        self.name = name
        
    def record(self, value, attributes=None):
        logger.debug(f"No-op histogram {self.name}.record({value}, {attributes})") 