"""
AutoTelemetry Library
-------------------

Cette bibliothèque fournit une auto-instrumentation pour les métriques, logs, et traces
dans les applications avec une seule ligne de code.
"""

from .autotelemetry import auto_instrument, LogLevel, Environment, SimpleObservabilityClient, DataLogger

__all__ = ["auto_instrument", "LogLevel", "Environment", "SimpleObservabilityClient", "DataLogger"]
__version__ = "0.1.0" 