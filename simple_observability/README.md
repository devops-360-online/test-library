# Simple Observability

A Python library that simplifies the use of OpenTelemetry for metrics, logs, and traces in data processing applications.

## Features

- **One-line setup** for all three pillars of observability (metrics, logs, traces)
- **Data-specific metrics** with pre-configured counters, gauges, and histograms
- **Automatic context propagation** between logs and traces
- **Decorators** for easy function instrumentation
- **Prometheus integration** for metrics visualization
- **OTLP support** for sending telemetry to collection backends

## Installation

```bash
pip install simple_observability
```

## Quick Start

```python
from simple_observability import ObservabilityClient
import pandas as pd

# Initialize the observability client
obs = ObservabilityClient(service_name="data-pipeline")

# Get a logger
logger = obs.get_logger()

# Use the data processing decorator
@obs.trace_data_processing()
def process_data(df):
    logger.info(f"Processing {len(df)} rows of data")
    # Your data processing logic here
    return df.dropna()

# Track a task with metrics and traces
def main():
    with obs.timed_task("data_processing", {"source": "example.csv"}) as ctx:
        # Create or get custom metrics if needed
        custom_metrics = obs.create_data_processing_metrics("custom")
        
        # Load data
        df = pd.read_csv("example.csv")
        logger.info(f"Loaded data with {len(df)} rows")
        
        # Record metrics
        custom_metrics["rows_processed"].add(len(df))
        
        # Process data with automatic tracing
        result = process_data(df)
        
        # Record more metrics
        custom_metrics["batch_size"].record(len(result))
        
        logger.info(f"Processing complete, {len(result)} rows after processing")

if __name__ == "__main__":
    try:
        main()
    finally:
        # Clean shutdown (also happens automatically with atexit)
        obs.shutdown()
```

## Visualizing Metrics with Prometheus and Grafana

This library automatically exposes metrics in Prometheus format. To visualize them:

1. Configure Prometheus to scrape your application
2. Add dashboards in Grafana that query your metrics

Example Prometheus configuration:

```yaml
scrape_configs:
  - job_name: 'data-pipeline'
    static_configs:
      - targets: ['localhost:8000']
```

## Distributed Tracing

For distributed tracing across multiple services:

1. Configure `otlp_endpoint` in the `ObservabilityClient`
2. Use a collector like OpenTelemetry Collector, Jaeger, or Zipkin
3. Visualize traces in your tracing backend

## Advanced Configuration

```python
# Full configuration example
obs = ObservabilityClient(
    service_name="data-pipeline",
    service_version="1.0.0",
    environment="production",
    prometheus_port=9090,
    log_level=logging.INFO,
    additional_attributes={
        "team": "data-science",
        "component": "feature-engineering"
    },
    otlp_endpoint="http://otel-collector:4317",
    enable_console_export=False
)
```

## Environment Variables

The library also supports configuration via environment variables:

- `SERVICE_VERSION`: Version of your service
- `ENVIRONMENT`: Deployment environment (dev, staging, prod)
- `PROMETHEUS_PORT`: Port for Prometheus metrics
- `LOG_LEVEL`: Logging level
- `OTLP_ENDPOINT`: Endpoint for OTLP exporter

## License

MIT 