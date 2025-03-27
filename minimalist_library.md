# AutoTelemetry - Bibliothèque Minimaliste d'Instrumentation

## Objectif

AutoTelemetry est une bibliothèque légère qui facilite l'instrumentation manuelle des applications Python en exposant simplement les outils OpenTelemetry de base (logger, tracer, métriques) aux développeurs.

## Principe

1. **Minimal**: Juste les interfaces essentielles pour l'observabilité
2. **Standardisé**: Formats et pratiques OpenTelemetry pour cohérence
3. **Manuel**: Contrôle total laissé aux développeurs
4. **Unifié**: Centralisation des configurations et exporteurs

## Installation

```bash
pip install autotelemetry
```

## Utilisation de Base

```python
from autotelemetry import ObservabilityTools

# Initialiser les outils avec configuration minimale
tools = ObservabilityTools(service_name="mon-application")

# Récupérer les outils individuels
logger = tools.get_logger()
tracer = tools.get_tracer()
meter = tools.get_meter()

# Utilisation manuelle selon les besoins
```

## Architecture Simplifiée

```
┌───────────────────────────────┐
│      ObservabilityTools       │
│                               │
│  ┌─────────┐ ┌─────┐ ┌──────┐ │
│  │ Logger  │ │Tracer│ │Meter │ │
│  └─────────┘ └─────┘ └──────┘ │
└───────────┬───────────────────┘
            │
┌───────────▼───────────────────┐
│      OpenTelemetry SDK        │
└───────────┬───────────────────┘
            │
┌───────────▼───────────────────┐
│    Exporteurs (Configurable)  │
│  Console | OTLP | Prometheus  │
└───────────────────────────────┘
```

## Composants

### 1. ObservabilityTools

Classe principale qui fournit les outils de base configurés:

```python
tools = ObservabilityTools(
    service_name="mon-application",  # Obligatoire
    service_version="1.0.0",         # Optionnel
    environment="production",        # Optionnel
    resource_attributes={"team": "data"},  # Optionnel
    otlp_endpoint="http://collector:4317",  # Optionnel
    prometheus_port=8000             # Optionnel
)
```

### 2. Logger

Logger standard avec support JSON optionnel:

```python
# Récupérer un logger
logger = tools.get_logger("nom-module")

# Utilisation manuelle standard
logger.info("Message simple")
logger.error("Une erreur s'est produite", exc_info=True)
logger.warning("Avertissement", extra={"data": {"key": "value"}})
```

### 3. Tracer

Tracer OpenTelemetry standard:

```python
# Récupérer un tracer
tracer = tools.get_tracer("nom-composant")

# Créer et gérer manuellement les spans
with tracer.start_as_current_span("opération") as span:
    # Ajouter attributs manuellement
    span.set_attribute("user.id", "12345")
    span.set_attribute("operation.type", "database-query")
    
    # Ajouter événement
    span.add_event("requête démarrée", {"query_id": "abc123"})
    
    # Effectuer l'opération...
    result = perform_operation()
    
    # Définir le statut (succès/échec)
    if error:
        span.set_status(Status(StatusCode.ERROR, "Erreur de connexion"))
    else:
        span.set_status(Status(StatusCode.OK))
```

### 4. Meter

Meter OpenTelemetry standard pour les métriques:

```python
# Récupérer un meter
meter = tools.get_meter("nom-composant")

# Créer et utiliser des compteurs manuellement
counter = meter.create_counter(
    name="requests.count",
    description="Nombre de requêtes",
    unit="1"
)
counter.add(1, {"endpoint": "/api", "method": "GET"})

# Créer et utiliser des histogrammes manuellement
histogram = meter.create_histogram(
    name="request.duration",
    description="Durée des requêtes",
    unit="ms"
)
histogram.record(42.5, {"endpoint": "/api", "status": 200})
```

## Exemples d'Utilisation

### Exemple de Service Web

```python
from flask import Flask, request
from autotelemetry import ObservabilityTools
import time

app = Flask(__name__)
tools = ObservabilityTools(service_name="api-service")

logger = tools.get_logger(__name__)
tracer = tools.get_tracer(__name__)
meter = tools.get_meter(__name__)

# Créer des métriques
request_counter = meter.create_counter("http.requests", "Nombre de requêtes HTTP", "1")
duration_histogram = meter.create_histogram("http.duration", "Durée des requêtes HTTP", "ms")

@app.route("/api/data")
def get_data():
    # Incrémenter le compteur de requêtes
    request_counter.add(1, {"path": "/api/data", "method": "GET"})
    
    # Créer un span pour la requête
    with tracer.start_as_current_span("http_request") as span:
        start_time = time.time()
        
        # Ajouter des attributs au span
        span.set_attribute("http.method", "GET")
        span.set_attribute("http.path", "/api/data")
        span.set_attribute("http.query_params", str(dict(request.args)))
        
        # Logger le début de la requête
        logger.info("Requête reçue", extra={
            "method": "GET",
            "path": "/api/data",
            "params": dict(request.args)
        })
        
        try:
            # Logique métier
            result = {"data": [1, 2, 3], "status": "success"}
            
            # Terminer avec succès
            span.set_status(Status(StatusCode.OK))
            return result
            
        except Exception as e:
            # Gérer l'erreur
            error_msg = str(e)
            logger.error(f"Erreur: {error_msg}", exc_info=True)
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, error_msg))
            return {"error": error_msg}, 500
            
        finally:
            # Enregistrer la durée
            duration_ms = (time.time() - start_time) * 1000
            duration_histogram.record(duration_ms, {"path": "/api/data", "method": "GET"})
```

### Exemple de Traitement de Données (avec instrumentation manuelle)

```python
import pandas as pd
from autotelemetry import ObservabilityTools

tools = ObservabilityTools(service_name="data-processor")
logger = tools.get_logger(__name__)
tracer = tools.get_tracer(__name__)
meter = tools.get_meter(__name__)

# Créer des métriques
rows_counter = meter.create_counter("data.rows", "Nombre de lignes traitées", "1")
process_histogram = meter.create_histogram("process.time", "Temps de traitement", "ms")

def process_data(filepath):
    # Créer un span parent pour tout le traitement
    with tracer.start_as_current_span("process_data") as main_span:
        main_span.set_attribute("file.path", filepath)
        logger.info(f"Traitement du fichier: {filepath}")
        
        # Span pour le chargement des données
        with tracer.start_as_current_span("load_data") as load_span:
            try:
                start_time = time.time()
                df = pd.read_csv(filepath)
                load_time = (time.time() - start_time) * 1000
                
                # Attributs de span
                rows = len(df)
                columns = len(df.columns)
                load_span.set_attribute("data.rows", rows)
                load_span.set_attribute("data.columns", columns)
                load_span.set_attribute("data.load_time_ms", load_time)
                
                # Métriques
                rows_counter.add(rows, {"operation": "load"})
                process_histogram.record(load_time, {"operation": "load"})
                
                # Log
                logger.info(f"Données chargées: {rows} lignes, {columns} colonnes", 
                           extra={"rows": rows, "columns": columns, "load_time_ms": load_time})
                
            except Exception as e:
                load_span.record_exception(e)
                load_span.set_status(Status(StatusCode.ERROR, str(e)))
                logger.error(f"Erreur de chargement: {str(e)}", exc_info=True)
                raise
        
        # Span pour le traitement
        with tracer.start_as_current_span("transform_data") as transform_span:
            try:
                start_time = time.time()
                
                # Filtrage
                df_filtered = df[df['value'] > 10]
                filtered_rows = len(df) - len(df_filtered)
                
                # Groupement
                result = df_filtered.groupby('category').mean()
                
                transform_time = (time.time() - start_time) * 1000
                
                # Attributs de span
                transform_span.set_attribute("data.input_rows", len(df))
                transform_span.set_attribute("data.output_rows", len(df_filtered))
                transform_span.set_attribute("data.filtered_rows", filtered_rows)
                transform_span.set_attribute("data.transform_time_ms", transform_time)
                
                # Métriques
                rows_counter.add(len(df_filtered), {"operation": "transform"})
                process_histogram.record(transform_time, {"operation": "transform"})
                
                # Log
                logger.info(f"Données transformées: {len(df_filtered)} lignes conservées, {filtered_rows} filtrées",
                           extra={"output_rows": len(df_filtered), "filtered_rows": filtered_rows})
                
                return result
                
            except Exception as e:
                transform_span.record_exception(e)
                transform_span.set_status(Status(StatusCode.ERROR, str(e)))
                logger.error(f"Erreur de transformation: {str(e)}", exc_info=True)
                raise
```

## Configuration Avancée

### Personnalisation des Exporteurs

```python
from autotelemetry import ObservabilityTools

# Configuration OTLP pour exporter vers un collecteur externe
tools = ObservabilityTools(
    service_name="mon-application",
    otlp_endpoint="http://collector:4317",
    otlp_protocol="grpc"  # ou "http/protobuf"
)

# Configuration Prometheus
tools = ObservabilityTools(
    service_name="mon-application",
    enable_prometheus=True,
    prometheus_port=9090
)

# Configuration des logs JSON
tools = ObservabilityTools(
    service_name="mon-application",
    enable_json_logs=True
)
```

### Personnalisation des Ressources

```python
tools = ObservabilityTools(
    service_name="mon-application",
    service_version="1.0.0",
    environment="production",
    resource_attributes={
        "deployment.region": "eu-west-1",
        "team": "data-engineering",
        "component": "processing-service"
    }
)
```

## Bonnes Pratiques

1. **Noms cohérents** : Utilisez des conventions de nommage cohérentes pour les spans, métriques et logs
2. **Attributs communs** : Partagez les mêmes attributs entre spans, logs et métriques pour faciliter la corrélation
3. **Hiérarchie de spans** : Créez une hiérarchie de spans (parent-enfant) pour représenter la structure d'exécution
4. **Statuts explicites** : Définissez toujours le statut des spans (OK/ERROR)
5. **Contexte d'erreur** : Enrichissez les spans et logs avec les détails des erreurs

## Conclusion

Cette bibliothèque minimaliste expose directement les interfaces OpenTelemetry tout en fournissant une configuration unifiée et cohérente. Elle laisse aux développeurs le contrôle total sur l'instrumentation tout en facilitant l'intégration avec les outils de monitoring. 