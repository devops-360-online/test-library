#!/usr/bin/env python3
"""
Exemple d'implémentation minimaliste d'AutoTelemetry

Ce fichier montre comment la bibliothèque pourrait être structurée
pour fournir juste les outils essentiels aux développeurs.
"""

import logging
import time
from typing import Dict, Any, Optional
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from prometheus_client import start_http_server


class ObservabilityTools:
    """
    Classe centrale qui configure et expose les outils d'observabilité.
    
    Cette classe minimaliste configure les trois piliers de l'observabilité
    et expose simplement les interfaces standard pour que les développeurs
    puissent les utiliser manuellement.
    """
    
    def __init__(
        self,
        service_name: str,
        service_version: str = "1.0.0",
        environment: str = "development",
        resource_attributes: Optional[Dict[str, Any]] = None,
        otlp_endpoint: Optional[str] = None,
        otlp_protocol: str = "grpc",
        enable_prometheus: bool = False,
        prometheus_port: int = 8000,
        enable_console_export: bool = True,
        enable_json_logs: bool = False,
    ):
        """
        Initialise les outils d'observabilité.
        
        Args:
            service_name: Nom du service (obligatoire)
            service_version: Version du service
            environment: Environnement (development, staging, production)
            resource_attributes: Attributs supplémentaires pour les ressources
            otlp_endpoint: Endpoint OTLP pour l'export de télémétrie
            otlp_protocol: Protocole OTLP (grpc ou http/protobuf)
            enable_prometheus: Activer l'export Prometheus
            prometheus_port: Port pour le serveur Prometheus
            enable_console_export: Activer l'export console (pour dev)
            enable_json_logs: Formater les logs en JSON
        """
        # Configurer la ressource
        attrs = {
            "service.name": service_name,
            "service.version": service_version,
            "deployment.environment": environment,
        }
        if resource_attributes:
            attrs.update(resource_attributes)
        
        self.resource = Resource.create(attrs)
        
        # Configurer le traçage
        self._setup_tracing(otlp_endpoint, enable_console_export)
        
        # Configurer les métriques
        self._setup_metrics(
            otlp_endpoint, 
            enable_prometheus, 
            prometheus_port, 
            enable_console_export
        )
        
        # Configurer les logs
        self._setup_logging(enable_json_logs)
        
        self.service_name = service_name
        self.service_info = {
            "service": service_name,
            "version": service_version,
            "environment": environment
        }
        
        logging.info(f"ObservabilityTools initialized for {service_name}")
    
    def _setup_tracing(self, otlp_endpoint: Optional[str], enable_console: bool):
        """Configure le provider de traçage et les exporteurs."""
        # Créer le provider
        trace_provider = TracerProvider(resource=self.resource)
        
        # Configurer les exporteurs
        if otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
            trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        
        if enable_console:
            console_exporter = ConsoleSpanExporter()
            trace_provider.add_span_processor(BatchSpanProcessor(console_exporter))
        
        # Définir le provider global
        trace.set_tracer_provider(trace_provider)
        self.tracer_provider = trace_provider
    
    def _setup_metrics(
        self, 
        otlp_endpoint: Optional[str], 
        enable_prometheus: bool,
        prometheus_port: int,
        enable_console: bool
    ):
        """Configure le provider de métriques et les exporteurs."""
        # Créer les readers/exporters
        metric_readers = []
        
        if otlp_endpoint:
            otlp_exporter = OTLPMetricExporter(endpoint=otlp_endpoint)
            otlp_reader = PeriodicExportingMetricReader(otlp_exporter)
            metric_readers.append(otlp_reader)
        
        if enable_prometheus:
            start_http_server(prometheus_port)
            prometheus_reader = PrometheusMetricReader()
            metric_readers.append(prometheus_reader)
        
        if enable_console:
            console_exporter = ConsoleMetricExporter()
            console_reader = PeriodicExportingMetricReader(console_exporter)
            metric_readers.append(console_reader)
        
        # Créer le provider
        meter_provider = MeterProvider(resource=self.resource, metric_readers=metric_readers)
        
        # Définir le provider global
        metrics.set_meter_provider(meter_provider)
        self.meter_provider = meter_provider
    
    def _setup_logging(self, enable_json: bool):
        """Configure le logging."""
        # Configuration de base du logging
        if enable_json:
            log_format = '{"timestamp":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","message":"%(message)s"}'
        else:
            log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def get_tracer(self, name: Optional[str] = None) -> trace.Tracer:
        """
        Obtient un tracer pour le module spécifié.
        
        Args:
            name: Nom du module/composant (par défaut: le nom du service)
            
        Returns:
            Un tracer OpenTelemetry configuré
        """
        tracer_name = name or self.service_name
        return trace.get_tracer(tracer_name)
    
    def get_meter(self, name: Optional[str] = None) -> metrics.Meter:
        """
        Obtient un meter pour le module spécifié.
        
        Args:
            name: Nom du module/composant (par défaut: le nom du service)
            
        Returns:
            Un meter OpenTelemetry configuré
        """
        meter_name = name or self.service_name
        return metrics.get_meter(meter_name)
    
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """
        Obtient un logger pour le module spécifié.
        
        Args:
            name: Nom du module/composant (par défaut: le nom du service)
            
        Returns:
            Un logger Python standard configuré
        """
        logger_name = name or self.service_name
        logger = logging.getLogger(logger_name)
        return logger


# Exemple d'utilisation
if __name__ == "__main__":
    # Initialiser les outils d'observabilité
    tools = ObservabilityTools(
        service_name="exemple-demo",
        enable_console_export=True
    )
    
    # Obtenir les outils individuels
    logger = tools.get_logger(__name__)
    tracer = tools.get_tracer(__name__)
    meter = tools.get_meter(__name__)
    
    # Créer des métriques personnalisées
    counter = meter.create_counter(
        name="demo.iterations", 
        description="Nombre d'itérations",
        unit="1"
    )
    histogram = meter.create_histogram(
        name="demo.processing_time",
        description="Temps de traitement",
        unit="ms"
    )
    
    # Simuler un processus avec instrumentation manuelle
    def process_item(item_id):
        logger.info(f"Traitement de l'item {item_id}")
        
        # Créer un span parent
        with tracer.start_as_current_span("process_item") as span:
            span.set_attribute("item.id", item_id)
            start_time = time.time()
            
            counter.add(1, {"item_id": str(item_id)})
            
            # Première étape
            with tracer.start_as_current_span("step_one") as step_span:
                logger.info("Étape 1 en cours...")
                step_span.set_attribute("step", "one")
                
                # Simuler un traitement
                time.sleep(0.1)
            
            # Deuxième étape
            with tracer.start_as_current_span("step_two") as step_span:
                logger.info("Étape 2 en cours...")
                step_span.set_attribute("step", "two")
                
                # Simuler un traitement
                time.sleep(0.2)
                
                if item_id % 5 == 0:
                    error_msg = f"Erreur simulée sur item {item_id}"
                    logger.error(error_msg)
                    step_span.record_exception(Exception(error_msg))
                    step_span.set_status(trace.Status(trace.StatusCode.ERROR, error_msg))
            
            # Calculer et enregistrer le temps de traitement
            duration_ms = (time.time() - start_time) * 1000
            histogram.record(duration_ms, {"item_id": str(item_id)})
            
            logger.info(f"Traitement terminé en {duration_ms:.2f} ms")
    
    # Traiter quelques items
    for i in range(10):
        process_item(i)
    
    logger.info("Traitement complet terminé")
    # La sortie console montrera les logs, traces et métriques 