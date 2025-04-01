#!/usr/bin/env python3
"""
Simple example showing how to attach logs to traces in OpenTelemetry
"""

import time
import random
import sys
import os

# Add the parent directory to the path so we can import mini_telemetry
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mini_telemetry import TelemetryTools

# Initialize telemetry with JSON logging to clearly see trace IDs
telemetry = TelemetryTools(
    service_name="simple-demo",
    service_version="1.0.0",
    environment="development",
    use_json_logs=True  # Using JSON format to clearly see trace IDs
)

# Get basic tools: tracer and logger
tracer = telemetry.get_tracer("demo.service")
logger = telemetry.get_logger("demo.service")

def process_item(item_id):
    """Process a single item with tracing and logging"""
    # Create a span (this starts a new trace or continues an existing one)
    with tracer.start_as_current_span(f"process_item") as span:
        # Add context information to the span
        span.set_attribute("item.id", item_id)
        
        # Log within the span context - this automatically includes trace_id and span_id
        logger.info(f"Starting to process item {item_id}")
        
        # Do some work
        time.sleep(random.uniform(0.1, 0.3))
        
        # Create a child span for a sub-operation
        with tracer.start_as_current_span("validate_item") as child_span:
            # Add attributes to the child span
            child_span.set_attribute("validation.type", "basic")
            
            # Log inside the child span - this will have the child span's ID
            logger.info(f"Validating item {item_id}")
            
            # Simulate work
            time.sleep(random.uniform(0.05, 0.1))
            
            # Log at different levels to show they all include trace context
            if item_id % 3 == 0:
                logger.warning(f"Item {item_id} requires special handling")
            
        # Back in the parent span
        logger.info(f"Completed processing for item {item_id}")

def main():
    """Run the demo"""
    logger.info("=== Starting Simple Trace with Logs Demo ===")
    
    # Process a few items to generate different traces
    for i in range(1, 4):
        process_item(i)
    
    logger.info("=== Demo Complete ===")

if __name__ == "__main__":
    main() 