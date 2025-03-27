"""
Simple Observability Library for Data Scripts
---------------------------------------------

This library provides a simple way to add metrics, logs, and traces to data scripts
using OpenTelemetry standards.
"""

from .observability import ObservabilityClient

__all__ = ["ObservabilityClient"]
__version__ = "0.1.0" 