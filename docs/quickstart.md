# Guide de Démarrage Rapide

Ce guide vous montre comment intégrer `simple_observability` dans votre application Python de traitement de données.

## Installation

Installez la bibliothèque via pip :

```bash
pip install simple_observability
```

## Utilisation basique

### Initialisation

```python
from simple_observability import ObservabilityClient

# Initialisation minimale
obs = ObservabilityClient(service_name="mon-service-de-donnees")

# Ou avec configuration complète
obs = ObservabilityClient(
    service_name="mon-service-de-donnees",
    service_version="1.0.0",
    environment="production",  # ou "development", "testing", "staging"
    prometheus_port=8000,      # port pour exposer les métriques
    otlp_endpoint="http://otel-collector:4317",  # pour envoyer les données à un collecteur
    json_logs=True             # format JSON pour les logs en production
)
```

### Logging avec contexte

```python
# Obtenir un logger
logger = obs.get_logger()

# Logging simple
logger.info("Démarrage du traitement")

# Logging avec contexte de données structuré
with logger.with_data(job_id="12345", batch_size=1000):
    logger.info("Traitement du lot de données")
    
    # Traitement...
    
    # Logging avec attributs supplémentaires
    logger.data(
        level=logging.INFO,
        msg="Statistiques de traitement",
        data={
            "rows_processed": 1000,
            "errors": 5,
            "duration_ms": 1200
        }
    )
```

### Traces et spans

```python
# Tracer une fonction automatiquement
@obs.trace_data_processing(attributes={"data_source": "database"})
def process_data(df):
    # Traitement...
    return result_df

# Utiliser un contexte d'opération standardisé
with obs.data_operation("load", "customer_table") as span:
    # Chargement de données...
    span.set_attribute("rows_loaded", 1000)

# Chronométrer une opération avec traces et métriques
with obs.timed_span("transformation", histogram=duration_histogram) as span:
    # Transformation de données...
    span.set_attribute("transformation_type", "normalization")
```

### Métriques

```python
# Créer des métriques standardisées pour le traitement de données
metrics = obs.create_data_processing_metrics(prefix="etl")

# Utilisation des métriques
metrics["rows_processed"].add(1000, {"job_id": "12345"})
metrics["processing_duration"].record(1.5, {"stage": "transform"})
metrics["memory_usage"].add(256 * 1024 * 1024)  # 256 MB

# Ou créer des métriques individuelles
counter = obs.create_counter(
    name="requests_total",
    description="Nombre total de requêtes",
    unit="1",
    attributes={"endpoint": "/api/data"}
)

histogram = obs.create_histogram(
    name="response_time_seconds",
    description="Temps de réponse en secondes",
    unit="s"
)
```

### Workflow complet

```python
def run_data_pipeline():
    # Créer des métriques standards
    metrics = obs.create_data_processing_metrics()
    
    # Utiliser un contexte de tâche avec métriques automatiques
    with obs.timed_task("pipeline_execution", {"pipeline_id": "daily-stats"}) as ctx:
        try:
            # Chargement des données
            with obs.data_operation("load", "source_table"):
                df = load_data()
                metrics["rows_processed"].add(len(df), {"stage": "load"})
            
            # Nettoyage des données
            with obs.data_operation("clean", "data_cleaning"):
                df_clean = clean_data(df)
                metrics["rows_processed"].add(len(df_clean), {"stage": "clean"})
            
            # Transformation
            with obs.data_operation("transform", "data_transform"):
                df_result = transform_data(df_clean)
                metrics["rows_processed"].add(len(df_result), {"stage": "transform"})
            
            # Écriture des résultats
            with obs.data_operation("save", "destination"):
                write_results(df_result)
                
            logger.info("Pipeline terminé avec succès")
            return True
            
        except Exception as e:
            logger.exception(f"Erreur dans le pipeline: {str(e)}")
            return False
```

## Configuration via variables d'environnement

La bibliothèque supporte la configuration via variables d'environnement :

```bash
# Configuration de base
export SERVICE_VERSION="1.0.0"
export ENVIRONMENT="production"

# Endpoints
export PROMETHEUS_PORT="9090"
export OTLP_ENDPOINT="http://collector:4317"

# Options de logging
export LOG_LEVEL="INFO"
export JSON_LOGS="true"
```

## Arrêt propre

```python
# Arrêt explicite pour vider les buffers de télémétrie
obs.shutdown()

# Ou avec atexit (activé par défaut)
import atexit
atexit.register(obs.shutdown)
```

## Intégration avec Prometheus et Grafana

1. Configurez Prometheus pour scraper les métriques exposées :

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'data-services'
    scrape_interval: 15s
    static_configs:
      - targets: ['app-host:8000']
```

2. Importez les dashboards Grafana fournis dans le répertoire [dashboards](../dashboards/).

## Prochaines étapes

- Consultez les [exemples complets](../examples/)
- Explorez l'[API de référence](api.md)
- Apprenez les [concepts fondamentaux](concepts.md) d'OpenTelemetry 