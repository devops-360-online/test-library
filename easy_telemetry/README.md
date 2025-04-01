# Easy Telemetry

A simple wrapper for OpenTelemetry in Python that makes it easy to add observability to your applications.

## Features

- Simple setup for tracing, metrics, and logging
- Automatic trace context propagation in logs
- JSON log formatting support
- Easy-to-use API for creating spans, metrics, and logs

## Installation

```bash
pip install easy-telemetry
```

## Quick Start

```python
from easy_telemetry import Telemetry

# Initialize telemetry
telemetry = Telemetry(
    service_name="my-service",
    service_version="1.0.0",
    environment="development"
)

# Get observability tools
logger = telemetry.get_logger()
tracer = telemetry.get_tracer()
meter = telemetry.get_meter()

# Use the tools
with tracer.start_as_current_span("my_operation") as span:
    logger.info("Starting operation")
    # Your code here
    logger.info("Operation complete")
```

## Documentation

### Configuration

The `Telemetry` class accepts the following parameters:

- `service_name`: Name of your service (required)
- `service_version`: Version of your service (default: "0.1.0")
- `environment`: Deployment environment (default: "development")
- `resource_attributes`: Additional resource attributes (optional)
- `log_level`: Minimum log level to capture (default: logging.INFO)
- `use_json_logs`: Whether to output logs in JSON format (default: False)

### Usage

1. **Logging**
```python
logger = telemetry.get_logger()
logger.info("This log will include trace context")
```

2. **Tracing**
```python
tracer = telemetry.get_tracer()
with tracer.start_as_current_span("operation") as span:
    span.set_attribute("key", "value")
    # Your code here
```

3. **Metrics**
```python
meter = telemetry.get_meter()
counter = meter.create_counter("my_counter")
counter.add(1)
```

## License

MIT License 