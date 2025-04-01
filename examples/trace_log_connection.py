#!/usr/bin/env python3
"""
This example clearly shows how logs are connected to trace contexts in OpenTelemetry.
It demonstrates the automatic correlation between logs and traces.
"""

import time
import sys
import os
import random

# Add the parent directory to the path so we can import mini_telemetry
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mini_telemetry import TelemetryTools

# Initialize telemetry with JSON logging to clearly see trace IDs
telemetry = TelemetryTools(
    service_name="trace-log-demo",
    service_version="1.0.0",
    environment="development",
    use_json_logs=True  # Using JSON format to clearly see trace IDs
)

# Get the tools we need
tracer = telemetry.get_tracer("trace.log.demo")
logger = telemetry.get_logger("trace.log.demo")

def show_log_trace_connection():
    """
    This function demonstrates how logs are automatically connected to traces
    through the OpenTelemetry context propagation mechanism.
    """
    logger.info("1. No trace context yet - this log won't have trace_id")
    
    # Start a trace
    with tracer.start_as_current_span("parent_operation") as parent_span:
        # These attributes will show up in the trace data
        parent_span.set_attribute("operation.id", "12345")
        parent_span.set_attribute("operation.name", "parent_operation")
        
        # This log will automatically pick up the trace_id and span_id from parent_span
        logger.info("2. Inside parent span - this log has parent trace_id and span_id")
        
        # Store the parent's IDs to show them in the output
        parent_trace_id = parent_span.get_span_context().trace_id
        parent_span_id = parent_span.get_span_context().span_id
        
        # Create a child span
        with tracer.start_as_current_span("child_operation") as child_span:
            # Add attributes to the child span
            child_span.set_attribute("operation.id", "67890")
            
            # This log will have the same trace_id as the parent but a different span_id
            logger.info("3. Inside child span - same trace_id but different span_id")
            
            # Store the child's IDs to show them in the output
            child_trace_id = child_span.get_span_context().trace_id
            child_span_id = child_span.get_span_context().span_id
            
            # Add an event to the child span (another way to add data)
            child_span.add_event(
                name="important_event", 
                attributes={"event.id": "event-123", "event.type": "demonstration"}
            )
            
            # Different log levels also carry trace context
            logger.warning("4. Warning log still has trace context!")
            
            # Simulate some work
            time.sleep(0.1)
        
        # This log is back in the parent span
        logger.info("5. Back to parent span - notice span_id changed back")
        
        # Show explicit values to make the connection clear
        logger.info(f"Connection overview - Parent span: trace_id={parent_trace_id:x}, span_id={parent_span_id:x}")
        logger.info(f"Connection overview - Child span: trace_id={child_trace_id:x}, span_id={child_span_id:x}")
    
    logger.info("6. Outside any span - no more trace context in logs")

def main():
    """Run the demonstration"""
    print("\n=== TRACE-LOG CONNECTION DEMO ===")
    print("This example shows how logs automatically connect to trace contexts")
    print("Watch for trace_id and span_id in the JSON logs\n")
    
    # Run the demo
    show_log_trace_connection()
    
    print("\n=== Trace and log data has been output above ===")
    print("Notice how the same trace_id appears in different logs, but span_id changes")
    print("This is how logs and traces are correlated in OpenTelemetry")

if __name__ == "__main__":
    main() 