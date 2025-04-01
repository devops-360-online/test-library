#!/usr/bin/env python3
"""
Mini-Telemetry - Simple observability library
---------------------------------------------

A lightweight library for application monitoring with:
1. Tracing - Track operations through your code
2. Logging - Record events with context
3. Metrics - Measure performance and behaviors

Requires no external dependencies and outputs to stdout.
"""

import json
import logging
import sys
import time
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable


class MiniTrace:
    """Simple tracing system to track operations through code."""
    
    def __init__(self, name: str):
        """Initialize tracer with a name."""
        self.name = name
        self.current_trace_id = None
        self.current_span_id = None
        self.parent_span_id = None
        self.spans = []
        self.active_spans = {}
    
    def generate_id(self) -> str:
        """Generate a random ID for traces and spans."""
        return str(uuid.uuid4())
    
    def start_trace(self) -> str:
        """Start a new trace and return the trace ID."""
        self.current_trace_id = self.generate_id()
        return self.current_trace_id
    
    def start_span(self, name: str, attributes: Dict[str, Any] = None) -> str:
        """Start a new span within the current trace."""
        if not self.current_trace_id:
            self.start_trace()
            
        span_id = self.generate_id()
        start_time = time.time()
        
        # Create span data
        span = {
            "trace_id": self.current_trace_id,
            "span_id": span_id,
            "parent_span_id": self.current_span_id,  # Could be None for root span
            "name": name,
            "start_time": start_time,
            "attributes": attributes or {},
            "events": []
        }
        
        # Save parent ID for restoration when span ends
        old_span_id = self.current_span_id
        
        # Set this as current span
        self.current_span_id = span_id
        
        # Store active span with its parent reference
        self.active_spans[span_id] = {
            "span": span,
            "parent_id": old_span_id
        }
        
        return span_id
    
    def end_span(self, span_id: Optional[str] = None) -> None:
        """End the specified span or current span if none provided."""
        if span_id is None:
            span_id = self.current_span_id
            
        if span_id not in self.active_spans:
            return
            
        # Get the span data
        span_data = self.active_spans[span_id]["span"]
        
        # Set end time
        span_data["end_time"] = time.time()
        span_data["duration_ms"] = (span_data["end_time"] - span_data["start_time"]) * 1000
        
        # Add to completed spans
        self.spans.append(span_data)
        
        # Restore parent span as current
        self.current_span_id = self.active_spans[span_id]["parent_id"]
        
        # Remove from active spans
        del self.active_spans[span_id]
        
        # If this was the root span, print the trace
        if not self.current_span_id:
            self._print_trace()
            self.current_trace_id = None
    
    def add_event(self, name: str, attributes: Dict[str, Any] = None) -> None:
        """Add an event to the current span."""
        if not self.current_span_id:
            return
            
        event = {
            "name": name,
            "timestamp": time.time(),
            "attributes": attributes or {}
        }
        
        # Add event to current span
        self.active_spans[self.current_span_id]["span"]["events"].append(event)
    
    def _print_trace(self) -> None:
        """Print the completed trace to stdout."""
        trace = {
            "trace_id": self.current_trace_id,
            "spans": self.spans
        }
        print(f"[TRACE] {json.dumps(trace)}")
        self.spans = []
    
    @contextmanager
    def span(self, name: str, attributes: Dict[str, Any] = None):
        """Context manager for spans."""
        span_id = self.start_span(name, attributes)
        try:
            yield span_id
        finally:
            self.end_span(span_id)


class MiniMetrics:
    """Simple metrics collection system."""
    
    def __init__(self, name: str):
        """Initialize metrics collector with a name."""
        self.name = name
        self.counters = {}
        self.gauges = {}
        self.histograms = {}
        self.last_report_time = time.time()
        self.report_interval = 10  # Report every 10 seconds by default
        
    def counter(self, name: str, value: int = 1, tags: Dict[str, str] = None) -> None:
        """Increment a counter metric."""
        key = self._get_key(name, tags)
        if key not in self.counters:
            self.counters[key] = {
                "name": name,
                "value": 0,
                "tags": tags or {}
            }
        self.counters[key]["value"] += value
        self._check_report()
    
    def gauge(self, name: str, value: float, tags: Dict[str, str] = None) -> None:
        """Set a gauge metric to a specific value."""
        key = self._get_key(name, tags)
        self.gauges[key] = {
            "name": name,
            "value": value,
            "tags": tags or {}
        }
        self._check_report()
    
    def histogram(self, name: str, value: float, tags: Dict[str, str] = None) -> None:
        """Record a value in a histogram metric."""
        key = self._get_key(name, tags)
        if key not in self.histograms:
            self.histograms[key] = {
                "name": name,
                "values": [],
                "tags": tags or {}
            }
        self.histograms[key]["values"].append(value)
        self._check_report()
    
    def _get_key(self, name: str, tags: Dict[str, str] = None) -> str:
        """Create a unique key for a metric based on its name and tags."""
        if not tags:
            return name
            
        # Sort tags for consistent keys
        sorted_tags = sorted(tags.items())
        tag_str = ",".join(f"{k}={v}" for k, v in sorted_tags)
        return f"{name}[{tag_str}]"
    
    def _check_report(self) -> None:
        """Check if it's time to report metrics."""
        now = time.time()
        if now - self.last_report_time >= self.report_interval:
            self.report()
            self.last_report_time = now
    
    def report(self) -> None:
        """Report all collected metrics."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "counters": list(self.counters.values()),
            "gauges": list(self.gauges.values()),
            "histograms": []
        }
        
        # Process histogram stats
        for h in self.histograms.values():
            values = h["values"]
            if not values:
                continue
                
            # Calculate basic stats
            sorted_values = sorted(values)
            hist_data = {
                "name": h["name"],
                "tags": h["tags"],
                "count": len(values),
                "sum": sum(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "p50": sorted_values[int(len(sorted_values) * 0.5)],
                "p90": sorted_values[int(len(sorted_values) * 0.9)],
                "p99": sorted_values[int(len(sorted_values) * 0.99)] if len(sorted_values) >= 100 else sorted_values[-1]
            }
            metrics["histograms"].append(hist_data)
            
        # Reset histograms after reporting
        self.histograms = {}
        
        # Print metrics to stdout
        print(f"[METRICS] {json.dumps(metrics)}")


class MiniLogger:
    """Simple logging system with context and trace integration."""
    
    LEVELS = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50
    }
    
    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[94m",     # Blue
        "INFO": "\033[92m",      # Green
        "WARNING": "\033[93m",   # Yellow
        "ERROR": "\033[91m",     # Red
        "CRITICAL": "\033[95m",  # Purple
        "RESET": "\033[0m"       # Reset
    }
    
    def __init__(self, name: str, level: str = "INFO", use_colors: bool = True):
        """Initialize logger with a name and minimum level."""
        self.name = name
        self.level = self.LEVELS.get(level.upper(), 20)
        self.use_colors = use_colors
        self.context = {}
        self.tracer = None
    
    def set_tracer(self, tracer: MiniTrace) -> None:
        """Associate a tracer with this logger for automatic trace context."""
        self.tracer = tracer
    
    def add_context(self, key: str, value: Any) -> 'MiniLogger':
        """Add context data to all subsequent log messages."""
        self.context[key] = value
        return self
    
    def update_context(self, data: Dict[str, Any]) -> 'MiniLogger':
        """Update multiple context values at once."""
        self.context.update(data)
        return self
    
    def clear_context(self) -> 'MiniLogger':
        """Clear all context data."""
        self.context.clear()
        return self
    
    def _log(self, level_name: str, message: str, extra: Dict[str, Any] = None) -> None:
        """Internal method to handle logging."""
        level_value = self.LEVELS.get(level_name, 0)
        if level_value < self.level:
            return
            
        # Build log data
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": level_name,
            "logger": self.name,
            "message": message
        }
        
        # Add context if available
        if self.context:
            log_data["context"] = self.context.copy()
            
        # Add trace context if available
        if self.tracer and self.tracer.current_trace_id:
            log_data["trace_id"] = self.tracer.current_trace_id
            log_data["span_id"] = self.tracer.current_span_id
            
        # Add extra data if provided
        if extra:
            for k, v in extra.items():
                # Don't overwrite existing fields
                if k not in log_data:
                    log_data[k] = v
        
        # Format as string for stdout
        if self.use_colors:
            color = self.COLORS.get(level_name, self.COLORS["RESET"])
            reset = self.COLORS["RESET"]
            log_str = f"{log_data['timestamp']} [{color}{level_name}{reset}] {self.name}: {message}"
        else:
            log_str = f"{log_data['timestamp']} [{level_name}] {self.name}: {message}"
            
        # Add trace/span info if available
        if self.tracer and self.tracer.current_trace_id:
            trace_id = self.tracer.current_trace_id
            span_id = self.tracer.current_span_id or "none"
            log_str += f" (trace={trace_id[:8]}... span={span_id[:8]}...)"
            
        print(log_str)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log a debug message."""
        self._log("DEBUG", message, kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log an info message."""
        self._log("INFO", message, kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log a warning message."""
        self._log("WARNING", message, kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log an error message."""
        self._log("ERROR", message, kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log a critical message."""
        self._log("CRITICAL", message, kwargs)
    
    @contextmanager
    def span_logger(self, name: str, level: str = "INFO", **span_attrs):
        """Create a logger that automatically creates a span for the duration of a context."""
        if not self.tracer:
            # Just yield self if no tracer is configured
            yield self
            return
            
        # Start span
        span_id = self.tracer.start_span(name, span_attrs)
        try:
            # Log the span start if level is sufficient
            self._log(level, f"Started {name}", span_attrs)
            yield self
        finally:
            # Log the span end
            duration = None
            if span_id in self.tracer.active_spans:
                start = self.tracer.active_spans[span_id]["span"]["start_time"]
                duration = int((time.time() - start) * 1000)
                
            self._log(level, f"Completed {name} in {duration}ms", span_attrs)
            self.tracer.end_span(span_id)


class MiniTelemetry:
    """Main entry point combining traces, metrics, and logs."""
    
    def __init__(
        self, 
        service_name: str,
        service_version: str = "1.0.0",
        environment: str = "development",
        log_level: str = "INFO",
        use_colors: bool = True,
        metrics_interval: int = 10
    ):
        """Initialize telemetry tools for a service."""
        self.service_name = service_name
        self.service_info = {
            "service": service_name,
            "version": service_version,
            "environment": environment
        }
        
        # Create the three pillars of observability
        self.tracer = MiniTrace(service_name)
        self.metrics = MiniMetrics(service_name)
        self.logger = MiniLogger(service_name, log_level, use_colors)
        
        # Set metrics reporting interval
        self.metrics.report_interval = metrics_interval
        
        # Connect logger and tracer for automatic context
        self.logger.set_tracer(self.tracer)
        self.logger.update_context(self.service_info)
        
        # Log initialization
        self.logger.info(f"MiniTelemetry initialized for {service_name} ({environment})")
    
    @contextmanager
    def trace(self, name: str, attributes=None, **kwargs):
        """Start a new trace or span, depending on context."""
        # Combine attributes dict and kwargs
        if attributes is None:
            attributes = {}
        if isinstance(attributes, dict):
            all_attrs = {**attributes, **kwargs}
        else:
            all_attrs = kwargs
            
        # Always include service info in traces
        trace_attrs = {**self.service_info, **all_attrs}
        
        # If no trace is active, start a new one
        new_trace = not self.tracer.current_trace_id
        if new_trace:
            self.tracer.start_trace()
            
        # Start the span
        span_id = self.tracer.start_span(name, trace_attrs)
        
        # Log span start, including span_id
        self.logger.info(f"Started {name}")
        
        try:
            yield span_id
        finally:
            end_time = time.time()
            if span_id in self.tracer.active_spans:
                start = self.tracer.active_spans[span_id]["span"]["start_time"]
                duration_ms = int((end_time - start) * 1000)
                # Log span end
                self.logger.info(f"Completed {name} in {duration_ms}ms")
                # Add duration metric
                self.metrics.histogram(
                    f"span.duration", 
                    duration_ms,
                    {"name": name, "service": self.service_name}
                )
            self.tracer.end_span(span_id)
    
    def count(self, name: str, value: int = 1, tags: Dict[str, str] = None) -> None:
        """Increment a counter metric."""
        if tags is None:
            tags = {}
        tags.update({"service": self.service_name})
        self.metrics.counter(name, value, tags)
    
    def gauge(self, name: str, value: float, tags: Dict[str, str] = None) -> None:
        """Set a gauge metric."""
        if tags is None:
            tags = {}
        tags.update({"service": self.service_name})
        self.metrics.gauge(name, value, tags)
    
    def timing(self, name: str, value_ms: float, tags: Dict[str, str] = None) -> None:
        """Record a timing metric."""
        if tags is None:
            tags = {}
        tags.update({"service": self.service_name})
        self.metrics.histogram(name, value_ms, tags)
    
    @contextmanager
    def timed(self, name: str, tags: Dict[str, str] = None):
        """Time a block of code and record the duration as a metric."""
        start = time.time()
        try:
            yield
        finally:
            duration_ms = (time.time() - start) * 1000
            self.timing(name, duration_ms, tags)


# Example usage
if __name__ == "__main__":
    # Initialize MiniTelemetry
    telemetry = MiniTelemetry("example-service", environment="dev")
    
    # Basic logging
    telemetry.logger.info("Application started")
    telemetry.logger.debug("Debug message")
    
    # Counter metric
    telemetry.count("app.start", 1)
    
    # Timing with automatic metrics
    with telemetry.timed("important_operation", {"type": "demo"}):
        # Creating a trace with spans
        with telemetry.trace("main_process"):
            telemetry.logger.info("Starting main process")
            time.sleep(0.1)
            
            # Nested span
            with telemetry.trace("sub_task", {"priority": "high"}):
                telemetry.logger.info("Working on subtask")
                telemetry.count("tasks.processed", 5)
                time.sleep(0.2)
                
            # Another operation
            with telemetry.trace("another_task"):
                telemetry.logger.warning("Task taking longer than expected")
                time.sleep(0.3)
                
    # Gauge metric
    telemetry.gauge("system.memory.usage", 42.5)
    
    # Force metrics report
    telemetry.metrics.report()
    
    telemetry.logger.info("Application finished")


