#!/usr/bin/env python3
"""
Mini-Telemetry - Bibliothèque minimaliste pour OpenTelemetry
------------------------------------------------------------

Cette bibliothèque simplifie l'utilisation d'OpenTelemetry en:
1. Configurant les outils de base (traces, logs, métriques)
2. Facilitant la corrélation entre ces signaux
3. Exposant une API simple pour les développeurs

LES DONNÉES SONT EXPORTÉES UNIQUEMENT VERS STDOUT:
- Aucun composant externe n'est nécessaire
- Tout apparaît directement dans la console
- Parfait pour le développement et le debug
- Un autre composant séparé peut collecter la sortie standard si nécessaire

Les développeurs sont responsables de l'instrumentation de leur code,
la bibliothèque ne fait que configurer et exposer les outils.
"""

import logging
import sys
import time
from typing import Dict, Any, Optional, List

# Import des modules OpenTelemetry de base
# - API: Interfaces publiques pour l'instrumentation
# - SDK: Implémentation des API pour collecter et exporter les données
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION, DEPLOYMENT_ENVIRONMENT

# Import pour l'intégration de contexte de trace dans les logs
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.trace import format_trace_id, format_span_id
import json


class TelemetryTools:
    """
    Classe centrale qui configure et expose les outils d'observabilité.
    
    Cette classe gère uniquement la configuration des outils OpenTelemetry
    et expose leurs interfaces pour que les développeurs puissent les utiliser
    dans leur code.
    """
    
    def __init__(
        self,
        service_name: str,                           # Nom du service (obligatoire)
        service_version: str = "1.0.0",              # Version du service
        environment: str = "development",            # Environnement (dev, staging, prod)
        resource_attributes: Optional[Dict] = None,  # Attributs supplémentaires
        log_level: int = logging.INFO,               # Niveau de log par défaut
        use_json_logs: bool = False                  # Format JSON pour les logs
    ):
        """
        Initialise les outils de télémétrie avec une configuration de base.
        
        Toute la configuration est faite ici, les développeurs n'ont plus qu'à
        utiliser les outils exposés.
        """
        # Stocker le nom du service pour référence ultérieure
        self.service_name = service_name
        self.service_info = {
            "service": service_name,
            "version": service_version,
            "environment": environment
        }
        
        # Étape 1: Configurer la ressource OpenTelemetry
        # La ressource identifie la source des données de télémétrie
        # et permet de les filtrer/organiser dans les outils d'analyse
        resource_attrs = {
            # Ces attributs sont standardisés par OpenTelemetry
            SERVICE_NAME: service_name,
            SERVICE_VERSION: service_version,
            DEPLOYMENT_ENVIRONMENT: environment
        }
        
        # Ajouter des attributs supplémentaires si fournis
        if resource_attributes:
            resource_attrs.update(resource_attributes)
        
        # Créer la ressource utilisée par tous les signaux
        self.resource = Resource.create(resource_attrs)
        
        # Étape 2: Configuration du traçage
        self._setup_tracing()
        
        # Étape 3: Configuration des métriques
        self._setup_metrics()
        
        # Étape 4: Configuration du logging (avec intégration trace)
        self._setup_logging(log_level, use_json_logs)
        
        # Initialiser le dictionnaire de contexte
        self._context_data = {}
        
        # Afficher un message d'initialisation
        self.logger.info(f"TelemetryTools initialisé pour {service_name}")
    
    def _setup_tracing(self):
        """
        Configure le système de traçage OpenTelemetry.
        
        Le traçage capture le chemin d'exécution à travers le code, les services
        et les systèmes distribués, sous forme de "spans".
        
        Export exclusivement vers stdout - aucun composant externe requis.
        """
        # Étape 1: Créer un provider de trace avec notre ressource
        # Le TracerProvider est le point d'entrée pour la création de tracers
        trace_provider = TracerProvider(resource=self.resource)
        
        # Étape 2: Configurer l'exportation des traces
        # ConsoleSpanExporter affiche les spans dans la sortie standard (stdout)
        # Aucune configuration supplémentaire ou composant externe n'est nécessaire
        console_exporter = ConsoleSpanExporter()
        
        # BatchSpanProcessor collecte les spans en mémoire et les exporte par lots
        # pour améliorer les performances
        span_processor = BatchSpanProcessor(console_exporter)
        trace_provider.add_span_processor(span_processor)
        
        # Étape 3: Définir ce provider comme provider global
        # Cela permet aux bibliothèques instrumentées d'utiliser ce provider
        trace.set_tracer_provider(trace_provider)
        
        # Conserver une référence au provider
        self.tracer_provider = trace_provider
        
        # Créer un tracer par défaut pour ce service
        self.tracer = trace.get_tracer(self.service_name)
        
        # Créer un propagateur pour extraire/injecter le contexte
        # Utilisé pour la corrélation avec les logs
        self.propagator = TraceContextTextMapPropagator()
    
    def _setup_metrics(self):
        """
        Configure le système de métriques OpenTelemetry.
        
        Les métriques capturent des données numériques comme des compteurs,
        des jauges et des histogrammes pour mesurer la performance et les états.
        
        Export exclusivement vers stdout - aucun composant externe requis.
        """
        # Étape 1: Configurer l'exportation des métriques
        # ConsoleMetricExporter affiche les métriques dans la sortie standard (stdout)
        # Aucune configuration supplémentaire ou composant externe n'est nécessaire
        console_exporter = ConsoleMetricExporter()
        
        # PeriodicExportingMetricReader collecte et exporte les métriques périodiquement
        reader = PeriodicExportingMetricReader(
            console_exporter,
            export_interval_millis=5000  # Exporter toutes les 5 secondes
        )
        
        # Étape 2: Créer un provider de métriques avec notre ressource
        meter_provider = MeterProvider(
            resource=self.resource,
            metric_readers=[reader]
        )
        
        # Étape 3: Définir ce provider comme provider global
        metrics.set_meter_provider(meter_provider)
        
        # Conserver une référence au provider
        self.meter_provider = meter_provider
        
        # Créer un meter par défaut pour ce service
        self.meter = metrics.get_meter(self.service_name)
    
    def _setup_logging(self, log_level: int, use_json: bool):
        """
        Configure le système de logging avec intégration de traces.
        
        L'intégration permet d'ajouter automatiquement les identifiants
        de trace et de span aux entrées de log correspondantes.
        
        Export exclusivement vers stdout - aucun composant externe requis.
        """
        # Étape 1: Créer un formateur de logs
        if use_json:
            # Format JSON pour les environnements de production
            # Facilite l'analyse avec des outils comme ELK
            formatter = JsonLogFormatter(self.tracer_provider)
        else:
            # Format texte pour le développement
            formatter = TraceContextFormatter(
                fmt='%(asctime)s [%(levelname)s] %(name)s - '
                    'trace_id=%(otel_trace_id)s span_id=%(otel_span_id)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        # Étape 2: Configurer le handler de base (stdout)
        # Les logs sont envoyés directement à la sortie standard
        # Aucun composant externe n'est nécessaire
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        
        # Étape 3: Configurer le logger root
        root_logger = logging.getLogger()
        root_logger.handlers = [handler]
        root_logger.setLevel(log_level)
        
        # Créer un logger par défaut pour ce service
        self.logger = logging.getLogger(self.service_name)
    
    def get_tracer(self, name: Optional[str] = None) -> trace.Tracer:
        """
        Obtient un tracer OpenTelemetry pour un module ou composant spécifique.
        
        Args:
            name: Nom du module/composant (default: nom du service)
            
        Returns:
            Un tracer OpenTelemetry configuré
        """
        tracer_name = name or self.service_name
        return trace.get_tracer(tracer_name)
    
    def get_meter(self, name: Optional[str] = None) -> metrics.Meter:
        """
        Obtient un meter OpenTelemetry pour un module ou composant spécifique.
        
        Args:
            name: Nom du module/composant (default: nom du service)
            
        Returns:
            Un meter OpenTelemetry configuré
        """
        meter_name = name or self.service_name
        return metrics.get_meter(meter_name)
    
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """
        Obtient un logger pour un module ou composant spécifique.
        
        Le logger est configuré pour inclure les IDs de traces dans les messages.
        
        Args:
            name: Nom du module/composant (default: nom du service)
            
        Returns:
            Un logger configuré
        """
        logger_name = name or self.service_name
        return logging.getLogger(logger_name)
    
    def set_context_data(self, key: str, value: Any) -> None:
        """
        Stocke une valeur dans le contexte de télémétrie.
        
        Args:
            key: Clé du contexte
            value: Valeur à stocker
        """
        self._context_data[key] = value
    
    def get_context_data(self, key: str, default: Any = None) -> Any:
        """
        Récupère une valeur du contexte de télémétrie.
        
        Args:
            key: Clé du contexte
            default: Valeur par défaut si la clé n'existe pas
            
        Returns:
            Valeur stockée ou valeur par défaut
        """
        return self._context_data.get(key, default)
    
    def clear_context_data(self) -> None:
        """
        Efface toutes les données de contexte.
        """
        self._context_data.clear()
    
    def update_context_data(self, context_dict: Dict[str, Any]) -> None:
        """
        Ajoute ou met à jour plusieurs valeurs dans le contexte de télémétrie.
        
        Args:
            context_dict: Dictionnaire de paires clé-valeur à ajouter au contexte
        """
        # Utiliser le span courant si disponible, sinon juste stocker les données
        span = trace.get_current_span()
        
        # Mettre à jour le contexte interne
        self._context_data.update(context_dict)
        
        # Si nous avons un span actif, ajouter aussi comme attributs
        if span.get_span_context().is_valid:
            for key, value in context_dict.items():
                span.set_attribute(key, value)


class TraceContextFormatter(logging.Formatter):
    """
    Formateur de logs qui ajoute automatiquement les ID de trace et de span.
    
    Cela permet la corrélation automatique entre logs et traces.
    """
    
    def format(self, record):
        """Format le message avec les informations de trace."""
        # Obtenir le span courant du contexte
        span_context = trace.get_current_span().get_span_context()
        
        # Ajouter les IDs au record si un span est actif
        if span_context.is_valid:
            # Formater les IDs en hexadécimal lisible
            record.otel_trace_id = format_trace_id(span_context.trace_id)
            record.otel_span_id = format_span_id(span_context.span_id)
        else:
            # Pas de span actif, utiliser des valeurs vides
            record.otel_trace_id = "0" * 16
            record.otel_span_id = "0" * 8
        
        # Formater le message avec le formateur parent
        return super().format(record)


class JsonLogFormatter(logging.Formatter):
    """
    Formateur de logs qui génère des messages JSON avec contexte de trace.
    
    Utile pour les environnements de production et l'analyse avec des outils comme ELK.
    """
    
    def __init__(self, tracer_provider=None):
        super().__init__()
        self.tracer_provider = tracer_provider
    
    def format(self, record):
        """Convertit l'enregistrement en JSON avec métadonnées de trace."""
        # Créer un dictionnaire de base avec les champs standard
        log_data = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage()
        }
        
        # Ajouter les données d'exception si présentes
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Ajouter les IDs de trace si disponibles
        span_context = trace.get_current_span().get_span_context()
        if span_context.is_valid:
            log_data["trace_id"] = format_trace_id(span_context.trace_id)
            log_data["span_id"] = format_span_id(span_context.span_id)
        
        # Convertir en JSON
        return json.dumps(log_data)


