"""
Simple Observability Library for Data Scripts
---------------------------------------------

This library provides automatic instrumentation for metrics, logs, and traces
in data applications with just a single line of code.
"""

from .simple_observability import auto_instrument

__all__ = ["auto_instrument"]
__version__ = "0.1.0" 