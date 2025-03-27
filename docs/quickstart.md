# Guide de démarrage rapide

Ce guide vous permettra de démarrer rapidement avec AutoTelemetry.

## Installation

```bash
pip install autotelemetry
```

## Utilisation basique

```python
from autotelemetry import auto_instrument, LogLevel, Environment

# Une seule ligne active l'observabilité complète
client = auto_instrument(
    service_name="mon-application",
    environment=Environment.PRODUCTION  # Les logs JSON sont obligatoires en production
)

# Le code après cette ligne est automatiquement instrumenté
```

## Configuration recommandée

Pour une configuration optimale, nous recommandons:

```python
from autotelemetry import auto_instrument, LogLevel, Environment

# Configuration complète
client = auto_instrument(
    service_name="mon-application",
    service_version="1.0.0",
    environment=Environment.PRODUCTION,  # Les logs JSON sont obligatoires en production
    log_level=LogLevel.INFO,
    additional_attributes={
        "team": "data-science",
        "domain": "recommandation"
    },
    prometheus_port=8000,
    otlp_endpoint="localhost:4317"  # Pour envoyer à un collecteur OpenTelemetry
)
```

## Utilisation des loggers

```python
# Obtenir un logger configuré
logger = client.get_logger()

# Log simple
logger.info("Traitement démarré")

# Log avec données structurées (disponible en JSON)
logger.info("Traitement terminé", data={
    "durée_ms": 350,
    "elements_traités": 1250,
    "erreurs": 0
})

# Log avec contexte temporaire
with logger.with_data(request_id="abc-123", utilisateur="user@example.com"):
    logger.info("Traitement de la requête")
    # Ces logs incluront automatiquement request_id et utilisateur
    logger.info("Étape intermédiaire")
```

## Créer des métriques personnalisées

```python
# Compteur
requetes_counter = client.create_counter(
    name="app.requetes.total",
    description="Nombre total de requêtes traitées",
    unit="1"
)

# Utilisation du compteur
requetes_counter.add(1, {"endpoint": "/api/data", "status": "success"})

# Histogramme pour la latence
latence_histogram = client.create_histogram(
    name="app.requetes.latence",
    description="Distribution des temps de réponse",
    unit="ms"
)

# Utilisation de l'histogramme
latence_histogram.record(42.5, {"endpoint": "/api/data"})
```

## Tracer des fonctions manuellement

L'auto-instrumentation trace la plupart des fonctions, mais vous pouvez également tracer manuellement:

```python
# Obtenir un tracer depuis le client
tracer = client.tracer

# Tracer un bloc de code
with tracer.start_as_current_span("opération.importante") as span:
    # Ajouter des attributs à la span
    span.set_attribute("priorité", "haute")
    
    # Exécuter l'opération
    résultat = effectuer_operation_importante()
    
    # Ajouter des informations sur le résultat
    span.set_attribute("taille_résultat", len(résultat))
```

## Fermeture propre

La bibliothèque enregistre un hook d'arrêt automatique, mais vous pouvez également fermer explicitement:

```python
# À la fin de votre programme
client.shutdown()
```

## Format JSON des logs

En production (environnement `Environment.PRODUCTION`), les logs JSON sont **obligatoires** et suivent cette structure:

```json
{
  "timestamp": "2023-09-10T15:42:10.123Z",
  "level": "INFO",
  "logger": "mon_module",
  "message": "Traitement terminé",
  "module": "mon_module",
  "function": "traiter_donnees",
  "line": 42,
  "service.name": "mon-application",
  "service.version": "1.0.0",
  "deployment.environment": "production",
  "trace_id": "abcdef1234567890abcdef1234567890",
  "span_id": "abcdef1234567890",
  "data": {
    "durée_ms": 350,
    "elements_traités": 1250
  }
}
```

Cette structure standardisée permet une analyse efficace dans des outils comme Elasticsearch ou Loki.

## Configuration via variables d'environnement

La bibliothèque supporte la configuration via variables d'environnement :

```bash
# Configuration de base
export SERVICE_NAME="mon-service"
export SERVICE_VERSION="1.0.0"
export ENVIRONMENT="production"

# Endpoints
export PROMETHEUS_PORT="9090"
export OTLP_ENDPOINT="http://collector:4317"

# Options de logging
export LOG_LEVEL="INFO"
export JSON_LOGS="true" # Toujours true en production
```

## Intégration avec Elasticsearch pour les logs JSON

Comme tous les logs sont en format JSON standardisé, ils s'intègrent parfaitement avec Elasticsearch :

```yaml
# logstash.conf
input {
  http {
    port => 8080
    codec => json
  }
}

filter {
  # Pas besoin de filtres complexes car les logs sont déjà structurés
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "logs-%{+YYYY.MM.dd}"
  }
}
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