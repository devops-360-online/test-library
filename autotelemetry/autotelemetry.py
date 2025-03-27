"""
Simple Observability - Bibliothèque simplifiée d'observabilité pour Python
--------------------------------------------------------------------------

Cette bibliothèque offre une auto-instrumentation immédiate avec une seule ligne de code,
standardisant les métriques, logs et traces pour les applications de traitement de données.
"""

import os
import sys
import time
import logging
import inspect
import importlib
import functools
import threading
import atexit
from typing import Dict, Any, Optional, Callable, List, TypeVar, cast

# OpenTelemetry imports
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_NAMESPACE, SERVICE_VERSION, DEPLOYMENT_ENVIRONMENT
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
try:
    from opentelemetry.exporter.prometheus import PrometheusMetricReader
    from prometheus_client import start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Type pour les fonctions décorées
F = TypeVar('F', bound=Callable[..., Any])

# Client global
_GLOBAL_CLIENT = None

# Standards pour les attributs
STANDARD_ATTR_SERVICE = "service.name"
STANDARD_ATTR_VERSION = "service.version"
STANDARD_ATTR_ENV = "deployment.environment"

# Standards pour les niveaux de log
class LogLevel:
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

# Standards pour les environnements
class Environment:
    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"

class DataLogger(logging.Logger):
    """
    Logger personnalisé avec support pour les données structurées.
    """
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        self._current_context = {}
    
    def with_data(self, **kwargs):
        """
        Retourne un context manager qui ajoute des données au contexte actuel.
        """
        return _LoggerContext(self, kwargs)
    
    def data(self, level, msg, data=None, *args, **kwargs):
        """
        Log un message avec des données structurées.
        """
        if self.isEnabledFor(level):
            # Combiner le contexte actuel avec les données spécifiques
            combined_data = {**self._current_context}
            if data:
                combined_data.update(data)
            
            # Ajouter les données au kwargs
            kwargs['extra'] = kwargs.get('extra', {})
            kwargs['extra']['data'] = combined_data
            
            # Log le message
            self._log(level, msg, args, **kwargs)

class _LoggerContext:
    """
    Context manager pour ajouter des données au contexte d'un logger.
    """
    def __init__(self, logger, data):
        self.logger = logger
        self.data = data
        self.previous_context = {}
    
    def __enter__(self):
        self.previous_context = self.logger._current_context.copy()
        self.logger._current_context.update(self.data)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger._current_context = self.previous_context

class JsonLogFormatter(logging.Formatter):
    """
    Formateur de logs au format JSON.
    """
    def __init__(self, trace_provider=None):
        super().__init__()
        self.trace_provider = trace_provider
    
    def format(self, record):
        import json
        
        # Données de base du log
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Ajouter le contexte de trace si disponible
        if self.trace_provider:
            current_span = trace.get_current_span()
            if current_span:
                context = current_span.get_span_context()
                if context:
                    log_data["trace_id"] = format(context.trace_id, '032x')
                    log_data["span_id"] = format(context.span_id, '016x')
        
        # Ajouter les données structurées si disponibles
        if hasattr(record, 'data'):
            log_data["data"] = record.data
        
        # Ajouter les informations d'exception
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        return json.dumps(log_data)

class SimpleObservabilityClient:
    """
    Client unifié pour l'observabilité.
    """
    def __init__(
        self,
        service_name: str,
        service_version: Optional[str] = None,
        environment: Optional[str] = None,
        prometheus_port: Optional[int] = None,
        log_level: Optional[int] = None,
        additional_attributes: Optional[Dict[str, str]] = None,
        otlp_endpoint: Optional[str] = None,
        enable_console_export: Optional[bool] = None,
        json_logs: Optional[bool] = None,
        auto_shutdown: bool = True,
    ):
        """
        Initialise le client d'observabilité.
        
        Args:
            service_name: Nom du service
            service_version: Version du service
            environment: Environnement (dev, test, staging, prod)
            prometheus_port: Port pour exposer les métriques Prometheus
            log_level: Niveau de log (valeurs de logging, ex: logging.INFO)
            additional_attributes: Attributs supplémentaires à ajouter à tous les signaux
            otlp_endpoint: Endpoint OTLP pour envoyer les données de télémétrie
            enable_console_export: Activer l'export vers la console
            json_logs: Utiliser le format JSON pour les logs
            auto_shutdown: Enregistrer automatiquement la fermeture propre
        """
        self.service_name = service_name
        self.service_version = service_version or os.environ.get("SERVICE_VERSION", "1.0.0")
        self.environment = environment or os.environ.get("ENVIRONMENT", Environment.DEVELOPMENT)
        self.prometheus_port = prometheus_port or int(os.environ.get("PROMETHEUS_PORT", "8000"))
        self.log_level = log_level or getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper())
        self.additional_attributes = additional_attributes or {}
        self.otlp_endpoint = otlp_endpoint or os.environ.get("OTLP_ENDPOINT", None)
        self.enable_console_export = enable_console_export or (self.environment == Environment.DEVELOPMENT)
        self.json_logs = json_logs or (self.environment == Environment.PRODUCTION)
        
        # Créer les ressources partagées
        self.resource = Resource.create({
            SERVICE_NAME: service_name,
            SERVICE_VERSION: self.service_version,
            DEPLOYMENT_ENVIRONMENT: self.environment,
            **self.additional_attributes
        })
        
        # Initialiser le tracing
        self._setup_tracing()
        
        # Initialiser les métriques
        self._setup_metrics()
        
        # Initialiser le logging
        self._setup_logging()
        
        # Obtenir un logger pour le client
        self.logger = self.get_logger()
        
        # Enregistrer l'arrêt propre
        if auto_shutdown:
            atexit.register(self.shutdown)
        
        self.logger.info(f"Observabilité initialisée pour {service_name}")
    
    def _setup_tracing(self):
        """Configure le tracing OpenTelemetry."""
        # Créer le provider de trace
        trace_provider = TracerProvider(resource=self.resource)
        
        # Ajouter les exportateurs
        if self.otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=self.otlp_endpoint)
            trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        
        if self.enable_console_export:
            console_exporter = ConsoleSpanExporter()
            trace_provider.add_span_processor(BatchSpanProcessor(console_exporter))
        
        # Définir le provider global
        trace.set_tracer_provider(trace_provider)
        
        # Créer un tracer pour cette bibliothèque
        self.tracer = trace.get_tracer("simple_observability", self.service_version)
    
    def _setup_metrics(self):
        """Configure les métriques OpenTelemetry."""
        # Créer la liste des lecteurs de métriques
        metric_readers = []
        
        # Ajouter l'exportateur OTLP si configuré
        if self.otlp_endpoint:
            otlp_exporter = OTLPMetricExporter(endpoint=self.otlp_endpoint)
            otlp_reader = PeriodicExportingMetricReader(otlp_exporter, export_interval_millis=10000)
            metric_readers.append(otlp_reader)
        
        # Ajouter l'exportateur console si activé
        if self.enable_console_export:
            console_exporter = ConsoleMetricExporter()
            console_reader = PeriodicExportingMetricReader(console_exporter, export_interval_millis=10000)
            metric_readers.append(console_reader)
        
        # Ajouter l'exportateur Prometheus si disponible
        if PROMETHEUS_AVAILABLE:
            prometheus_reader = PrometheusMetricReader()
            metric_readers.append(prometheus_reader)
            start_http_server(self.prometheus_port)
        
        # Créer le provider de métriques
        meter_provider = MeterProvider(resource=self.resource, metric_readers=metric_readers)
        metrics.set_meter_provider(meter_provider)
        
        # Créer un meter pour cette bibliothèque
        self.meter = metrics.get_meter("simple_observability", self.service_version)
    
    def _setup_logging(self):
        """Configure le logging."""
        # Remplacer la classe de Logger par défaut
        logging.setLoggerClass(DataLogger)
        
        # Configurer le logger racine
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # Supprimer les handlers existants
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Créer un handler console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        
        # Configurer le formateur selon le mode
        if self.json_logs:
            formatter = JsonLogFormatter(trace.get_tracer_provider())
        else:
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            if hasattr(formatter, 'default_msec_format'):
                formatter.default_msec_format = '%s.%03d'
        
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    def get_logger(self, name=None):
        """
        Obtient un logger configuré.
        
        Args:
            name: Nom du logger (par défaut: nom du module appelant)
            
        Returns:
            Un logger configuré
        """
        if name is None:
            # Si aucun nom n'est fourni, utiliser le nom du module appelant
            frame = inspect.currentframe().f_back
            name = frame.f_globals['__name__']
        
        return logging.getLogger(name)
    
    def create_counter(self, name, description=None, unit=None, attributes=None):
        """
        Crée un compteur.
        
        Args:
            name: Nom du compteur
            description: Description du compteur
            unit: Unité de mesure
            attributes: Attributs par défaut
            
        Returns:
            Un compteur
        """
        return self.meter.create_counter(
            name=name,
            description=description,
            unit=unit
        )
    
    def create_histogram(self, name, description=None, unit=None, attributes=None):
        """
        Crée un histogramme.
        
        Args:
            name: Nom de l'histogramme
            description: Description de l'histogramme
            unit: Unité de mesure
            attributes: Attributs par défaut
            
        Returns:
            Un histogramme
        """
        return self.meter.create_histogram(
            name=name,
            description=description,
            unit=unit
        )
    
    def create_system_metrics(self):
        """
        Crée des métriques système standard.
        
        Returns:
            Un dictionnaire de métriques système
        """
        metrics = {
            "cpu_usage": self.create_histogram(
                name="system.cpu.usage",
                description="Utilisation CPU en pourcentage",
                unit="%"
            ),
            "memory_usage": self.create_histogram(
                name="system.memory.usage",
                description="Utilisation mémoire en bytes",
                unit="By"
            ),
            "gc_count": self.create_counter(
                name="system.gc.count",
                description="Nombre de collections du garbage collector",
                unit="1"
            ),
            "gc_duration": self.create_histogram(
                name="system.gc.duration",
                description="Durée des collections du garbage collector",
                unit="ms"
            )
        }
        return metrics
    
    def start_system_metrics_collection(self, metrics):
        """
        Démarre la collecte périodique des métriques système.
        
        Args:
            metrics: Dictionnaire de métriques système
        """
        import psutil
        import gc
        
        def collect_metrics():
            try:
                while True:
                    # Collecter CPU
                    cpu_percent = psutil.cpu_percent(interval=1)
                    metrics["cpu_usage"].record(cpu_percent)
                    
                    # Collecter mémoire
                    memory = psutil.Process().memory_info()
                    metrics["memory_usage"].record(memory.rss)
                    
                    # Collecter GC stats si disponible
                    gc_counts = gc.get_count()
                    for i, count in enumerate(gc_counts):
                        metrics["gc_count"].add(count, {"generation": str(i)})
                    
                    # Pause entre collections
                    time.sleep(10)
            except Exception as e:
                self.logger.exception(f"Erreur dans la collecte des métriques système: {str(e)}")
        
        # Démarrer dans un thread séparé
        thread = threading.Thread(target=collect_metrics, daemon=True)
        thread.start()
    
    def shutdown(self):
        """
        Arrête proprement le client d'observabilité.
        
        Cette méthode est appelée automatiquement à la fin du programme
        si auto_shutdown=True.
        """
        self.logger.info("Arrêt propre de l'observabilité")
        
        # Obtenir les providers
        tracer_provider = trace.get_tracer_provider()
        meter_provider = metrics.get_meter_provider()
        
        # Fermer les providers
        if hasattr(tracer_provider, "shutdown"):
            tracer_provider.shutdown()
        
        if hasattr(meter_provider, "shutdown"):
            meter_provider.shutdown()

# Fonctions d'auto-instrumentation

def auto_instrument(
    service_name: str,
    service_version: Optional[str] = None,
    environment: Optional[str] = None,
    prometheus_port: Optional[int] = None,
    log_level: Optional[int] = None,
    additional_attributes: Optional[Dict[str, str]] = None,
    otlp_endpoint: Optional[str] = None,
    enable_console_export: Optional[bool] = None,
    json_logs: Optional[bool] = None,
    auto_shutdown: bool = True,
):
    """
    Active automatiquement toutes les fonctionnalités d'observabilité avec une seule ligne.
    
    Cette fonction:
    1. Initialise le client d'observabilité global
    2. Configure les exportateurs de télémétrie
    3. Configure le logging structuré
    4. Instrumente automatiquement toutes les fonctions nouvellement définies
    5. Collecte automatiquement les métriques système
    6. Enregistre un hook d'arrêt propre
    
    Args:
        service_name: Nom du service
        service_version: Version du service (optionnel)
        environment: Environnement (dev, test, staging, prod)
        prometheus_port: Port pour exposer les métriques Prometheus
        log_level: Niveau de log (valeurs de logging, ex: logging.INFO)
        additional_attributes: Attributs supplémentaires à ajouter à tous les signaux
        otlp_endpoint: Endpoint OTLP pour envoyer les données de télémétrie
        enable_console_export: Activer l'export vers la console
        json_logs: Utiliser le format JSON pour les logs
        auto_shutdown: Enregistrer automatiquement la fermeture propre
    
    Returns:
        Le client d'observabilité
    """
    global _GLOBAL_CLIENT
    
    # Initialiser le client global s'il n'existe pas déjà
    if _GLOBAL_CLIENT is None:
        _GLOBAL_CLIENT = SimpleObservabilityClient(
            service_name=service_name,
            service_version=service_version,
            environment=environment,
            prometheus_port=prometheus_port,
            log_level=log_level,
            additional_attributes=additional_attributes,
            otlp_endpoint=otlp_endpoint,
            enable_console_export=enable_console_export,
            json_logs=json_logs,
            auto_shutdown=auto_shutdown,
        )
        
        # Appliquer l'auto-instrumentation
        _apply_auto_instrumentation()
        
        # Collecter les métriques système
        _setup_system_metrics()
        
        # Instrumenter les bibliothèques de data science
        _setup_data_science_instrumentation()
        
        _GLOBAL_CLIENT.logger.info(f"Auto-instrumentation activée pour {service_name}")
        
        if auto_shutdown:
            atexit.register(_shutdown)
    
    return _GLOBAL_CLIENT

def _shutdown():
    """Arrête proprement le client d'observabilité."""
    global _GLOBAL_CLIENT
    if _GLOBAL_CLIENT is not None:
        _GLOBAL_CLIENT.shutdown()

def _function_decorator(func: F) -> F:
    """
    Decorator that automatically creates spans for functions.
    It will set span name to the function name and add relevant attributes.
    """
    import functools
    import inspect
    import threading

    # Create thread-local storage for call stack tracking
    _local = threading.local()
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Initialize call stack for this thread if it doesn't exist
        if not hasattr(_local, 'call_stack'):
            _local.call_stack = set()
            
        # Get function's qualified name
        func_name = f"{func.__module__}.{func.__qualname__}"
        
        # Check if we're already tracing this function to prevent recursion
        if func_name in _local.call_stack:
            # Already tracing this function, just execute it without creating a new span
            return func(*args, **kwargs)
            
        # Add to call stack before creating span
        _local.call_stack.add(func_name)
        
        try:
            # Get function signature and argument values
            try:
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                arg_dict = dict(bound_args.arguments)
                # Convert non-primitive types to strings to prevent serialization issues
                for k, v in arg_dict.items():
                    if not isinstance(v, (str, int, float, bool, type(None))):
                        arg_dict[k] = f"{type(v).__name__}"
            except Exception:
                # If we can't inspect arguments, just use empty dict
                arg_dict = {}

            # Get the tracer and create a span
            if _GLOBAL_CLIENT is None:
                return func(*args, **kwargs)
                
            tracer = _GLOBAL_CLIENT.tracer
            with tracer.start_as_current_span(
                name=func_name,
                attributes={
                    "code.function": func.__name__,
                    "code.namespace": func.__module__,
                    "code.arguments": str(arg_dict)
                }
            ) as span:
                # Execute the wrapped function
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    # Record the exception in the span
                    span.record_exception(e)
                    # Re-raise the exception
                    raise
        finally:
            # Always remove from call stack, even if an exception occurs
            _local.call_stack.remove(func_name)

    # Mark this function as instrumented to avoid double instrumentation
    wrapper._auto_instrumented = True
    
    return cast(F, wrapper)

def _apply_auto_instrumentation():
    """
    Applique l'auto-instrumentation en modifiant le mécanisme d'import Python.
    
    Cette fonction installe un hook d'import qui décore automatiquement
    toutes les fonctions nouvellement définies dans les modules importés.
    """
    # Installer le hook d'import
    sys.meta_path.insert(0, AutoInstrumentImportFinder())
    
    # Instrumenter les modules déjà chargés
    for module_name, module in list(sys.modules.items()):
        if not module_name.startswith('_') and not module_name.startswith('simple_observability'):
            _instrument_module(module)

def _instrument_module(module):
    """
    Instrumente un module existant.
    """
    if module is None:
        return
        
    for attr_name in dir(module):
        if attr_name.startswith('_'):
            continue
            
        try:
            attr = getattr(module, attr_name)
            
            # Skip already instrumented functions
            if hasattr(attr, '_auto_instrumented'):
                continue
                
            # Instrumenter seulement les fonctions et méthodes
            if inspect.isfunction(attr) or inspect.ismethod(attr):
                setattr(module, attr_name, _function_decorator(attr))
                
            # Instrumenter les classes (leurs méthodes)
            elif inspect.isclass(attr):
                for method_name in dir(attr):
                    if method_name.startswith('_'):
                        continue
                        
                    try:
                        method = getattr(attr, method_name)
                        # Skip already instrumented methods
                        if hasattr(method, '_auto_instrumented'):
                            continue
                            
                        if inspect.isfunction(method) or inspect.ismethod(method):
                            setattr(attr, method_name, _function_decorator(method))
                    except (AttributeError, TypeError):
                        pass
        except (AttributeError, TypeError):
            pass

class AutoInstrumentImportFinder:
    """
    Finder pour l'auto-instrumentation des imports.
    """
    def __init__(self):
        self.original_meta_path = sys.meta_path[:]
    
    def find_spec(self, fullname, path, target=None):
        # Trouver le spec original
        for finder in self.original_meta_path:
            if finder is self:
                continue
            try:
                spec = finder.find_spec(fullname, path, target)
                if spec is not None:
                    return spec
            except (AttributeError, ImportError):
                continue
        return None
    
    def find_module(self, fullname, path=None):
        # Pour compatibilité avec Python < 3.4
        for finder in self.original_meta_path:
            if finder is self:
                continue
            try:
                loader = finder.find_module(fullname, path)
                if loader is not None:
                    return loader
            except (AttributeError, ImportError):
                continue
        return None
    
    def load_module(self, name):
        module = importlib.import_module(name)
        _instrument_module(module)
        return module

def _setup_system_metrics():
    """
    Configure les métriques système automatiques.
    """
    if _GLOBAL_CLIENT is None:
        return
        
    # Créer des métriques pour CPU, mémoire, etc.
    metrics = _GLOBAL_CLIENT.create_system_metrics()
    
    # Démarrer la collecte périodique
    _GLOBAL_CLIENT.start_system_metrics_collection(metrics)

def _setup_data_science_instrumentation():
    """
    Ajoute une instrumentation spécifique pour les bibliothèques de data science.
    """
    if _GLOBAL_CLIENT is None:
        return
    
    # Instrumenter Pandas
    try:
        import pandas
        
        # Patch pour les opérations pandas courantes
        original_read_csv = pandas.read_csv
        
        @functools.wraps(original_read_csv)
        def patched_read_csv(*args, **kwargs):
            if _GLOBAL_CLIENT is not None:
                with _GLOBAL_CLIENT.tracer.start_as_current_span("pandas.read_csv") as span:
                    try:
                        result = original_read_csv(*args, **kwargs)
                        if hasattr(result, "shape"):
                            span.set_attribute("pandas.rows", result.shape[0])
                            span.set_attribute("pandas.columns", result.shape[1])
                        return result
                    except Exception as e:
                        if span:
                            span.record_exception(e)
                            span.set_status(Status(
                                status_code=StatusCode.ERROR,
                                description=str(e)
                            ))
                        raise
            else:
                return original_read_csv(*args, **kwargs)
        
        pandas.read_csv = patched_read_csv
        
        # Instrumenter d'autres fonctions pandas...
        
    except ImportError:
        # Pandas n'est pas installé
        pass
    
    # Instrumenter NumPy
    try:
        import numpy
        # Instrumenter les opérations numpy...
    except ImportError:
        pass
    
    # Instrumenter Scikit-learn
    try:
        import sklearn
        # Instrumenter les estimateurs scikit-learn...
    except ImportError:
        pass 