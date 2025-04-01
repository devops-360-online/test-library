#!/usr/bin/env python3
"""
Demonstration of adding logs directly to spans as events
This shows how to make log messages part of the span data structure itself
"""

import time
import sys
import os

# Add the parent directory to the path so we can import mini_telemetry
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mini_telemetry import TelemetryTools
from opentelemetry import trace

# Initialize telemetry
telemetry = TelemetryTools(
    service_name="span-events-demo",
    service_version="1.0.0",
    environment="development"
)

# Get basic tools
tracer = telemetry.get_tracer("span.events.demo")
logger = telemetry.get_logger("span.events.demo")

def log_to_span(span, level, message, **attributes):
    """
    Add a log message directly to a span as an event
    
    Args:
        span: The span to add the log to
        level: Log level (INFO, WARNING, ERROR, etc.)
        message: The log message
        **attributes: Additional attributes to add to the event
    """
    # Create a base set of attributes for the event
    event_attributes = {
        "log.level": level,
        "log.message": message
    }
    
    # Add any additional attributes
    event_attributes.update(attributes)
    
    # Add the event to the span
    span.add_event(f"log.{level.lower()}", event_attributes)
    
    # Also log through the regular logger for console output
    if level == "INFO":
        logger.info(message)
    elif level == "WARNING":
        logger.warning(message)
    elif level == "ERROR":
        logger.error(message)

def process_with_span_logs():
    """
    Demonstrate how to add logs directly to spans as events
    
    This approach makes logs part of the span data itself,
    rather than separate log entries that are correlated.
    """
    print("\nStarting span with direct log events...")
    
    # Start a span
    with tracer.start_as_current_span("process_with_events") as span:
        # Add logs directly to the span as events
        log_to_span(span, "INFO", "Starting process", process_id=123)
        
        # Simulate some work
        time.sleep(0.2)
        
        # Log a warning directly to the span
        log_to_span(span, "WARNING", "Resource usage high", cpu_usage=85, memory_usage=75)
        
        # Create a child span
        with tracer.start_as_current_span("sub_process") as child_span:
            # Log to the child span
            log_to_span(child_span, "INFO", "Sub-process started", sub_process_id=456)
            
            # Simulate an error condition
            try:
                # Simulate work that fails
                time.sleep(0.1)
                raise ValueError("Simulated error in sub-process")
            except Exception as e:
                # Log the error directly to the span
                log_to_span(
                    child_span, 
                    "ERROR", 
                    f"Sub-process failed: {str(e)}", 
                    exception_type=type(e).__name__
                )
                
                # Set the span status to error
                child_span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            
            # Finish the child span with a final log
            log_to_span(child_span, "INFO", "Sub-process complete (with error)")
        
        # Back to the parent span
        log_to_span(span, "INFO", "Process complete", status="with_errors")

def main():
    """Run the demonstration"""
    print("=== LOGS AS SPAN EVENTS DEMO ===")
    print("This example shows how to add logs directly to spans as events")
    print("Look at the span data to see the log events attached to spans")
    
    # Run the demo
    process_with_span_logs()
    
    print("\n=== Demo Complete ===")
    print("Notice how the log entries appear as events within the span data")
    print("This makes logs an integral part of the span rather than just correlated")

if __name__ == "__main__":
    main() 