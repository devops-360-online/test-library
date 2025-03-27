# Documentation AutoTelemetry

## Introduction

AutoTelemetry est une bibliothèque d'observabilité qui simplifie radicalement l'instrumentation des applications Python, en particulier pour les applications de traitement de données. Elle offre une intégration transparente des trois piliers de l'observabilité (métriques, logs, traces) en une seule API unifiée.

## Principes de Conception

1. **Simplicité**: Activation complète en une seule ligne de code
2. **Standardisation**: Format JSON pour tous les logs, standards OpenTelemetry
3. **Auto-instrumentation**: Instrumentation automatique des fonctions et bibliothèques
4. **Données structurées**: Support natif pour les logs avec contexte enrichi
5. **Vue unifiée**: Corrélation automatique entre métriques, logs et traces

## Fonctionnalités Clés

- **Auto-instrumentation complète**: Instrumentation automatique de toutes les fonctions
- **Logs JSON structurés**: Format standard pour faciliter l'analyse
- **Métriques Prometheus**: Exposition automatique des métriques
- **Traces OpenTelemetry**: Traçage automatique des fonctions et appels
- **Instrumentation spéciale pour le traitement de données**: Support pour Pandas, NumPy
- **Métriques de données intelligentes**: Capture des volumes de données traitées

## Architecture

![Architecture](https://mermaid.ink/img/pako:eNp1kk1PwzAMhv9KlBOgSvs6cJkEEkgcmLhwQT1ETbpoaNKqScoG1f47aReGhrg4r-znteOP-Q5LLYBlLJVNJQ5kL0ahDfaIpVtLMdLFQdcmNvpRO2xUUQddrW2LLsXORoJKGzBdrdmDG3GbB5z_8OdHrrpgQ9nSFOb9OjIgZc95U7jGQJGcEfRm0ZVl2GDVhELLU9_QHvVYLkbpRQTm06vwXp42Ryt6hL4JbUw7ZUXx9Bz0eGKbzH2KX1qYVjePTOcXVaM_UMgPKBRRKKMwtQzw1D6cVmGn3sRoG1XoFrHUTTRnZxOV3E6NSaROOBl5Qxev9iR3JlN5KDJ0U-p5jHu9Y7Fvfz0gGjMrVEI3VxnkdaodZh_8nQNQwN9P3gW2A1T-Cf89e-fOV9Kh6YYVuxBdMtapS_ahJjfQprMhwzKIGeeVrxrhqXx6cDnQKdDZuZ2BZVkf9Kn5tS3-Cp8LlgubUyesP14tE_g)

## Installation

```bash
pip install autotelemetry
```

## Guide d'Utilisation

### Initialisation de base

```python
from autotelemetry import auto_instrument

# Une seule ligne active toute l'observabilité
client = auto_instrument(service_name="mon-application")
```

### Configuration Avancée

```python
from autotelemetry import auto_instrument, Environment, LogLevel

client = auto_instrument(
    service_name="mon-application",
    service_version="1.0.0",
    environment=Environment.PRODUCTION,  # PRODUCTION force les logs JSON
    log_level=LogLevel.INFO,
    prometheus_port=8080,
    otlp_endpoint="http://collector:4317",  # Pour exporter vers un collecteur OpenTelemetry
    additional_attributes={"team": "data-engineering"}
)
```

### Logging Structuré

```python
# Obtenir un logger
logger = client.get_logger()

# Log simple
logger.info("Opération démarrée")

# Log avec contexte structuré
logger.info("Traitement des données terminé", extra={"data": {
    "rows_processed": 1500,
    "duration_ms": 342,
    "status": "success"
}})

# Niveaux de log disponibles
logger.debug("Message de débogage")
logger.info("Message d'information")
logger.warning("Avertissement")
logger.error("Erreur")
logger.critical("Erreur critique")
```

### Métriques Personnalisées

```python
# Créer un compteur (pour des valeurs qui ne peuvent qu'augmenter)
requests_counter = client.create_counter(
    name="app.requests.count",
    description="Nombre total de requêtes traitées",
    unit="1"  # Nombre d'items (sans unité)
)

# Incrémenter le compteur, potentiellement avec des attributs
requests_counter.add(1, {"endpoint": "/api/data", "method": "GET"})

# Créer un histogramme (pour des distributions de valeurs)
response_time = client.create_histogram(
    name="app.response.time",
    description="Temps de réponse des requêtes",
    unit="ms"  # Millisecondes
)

# Enregistrer une valeur dans l'histogramme
response_time.record(42.5, {"endpoint": "/api/data", "status": "success"})
```

### Tracing Manuel

En plus du tracing automatique, vous pouvez créer des spans manuels:

```python
# Obtenir le tracer
tracer = client.tracer

# Créer un span
with tracer.start_as_current_span("opération-personnalisée") as span:
    # Ajouter des attributs au span
    span.set_attribute("user.id", "1234")
    span.set_attribute("operation.type", "data-export")
    
    # Logique métier...
    
    # Créer un événement dans le span
    span.add_event("checkpoint", {"progress": "50%"})
    
    # Sous-opération (créera un span enfant)
    with tracer.start_as_current_span("sous-opération") as child_span:
        # Logique de la sous-opération...
        pass
```

### Auto-Instrumentation des Bibliothèques de Données

La bibliothèque instrumente automatiquement Pandas et NumPy:

```python
import pandas as pd
import numpy as np

# Ces opérations sont automatiquement tracées
df = pd.read_csv("data.csv")  # Génère des métriques sur le nombre de lignes

# Opérations de traitement
df_filtered = df[df['value'] > 10]  # Trace les lignes filtrées
result = df.groupby('category').mean()  # Trace l'agrégation

# Opérations NumPy
mean = np.mean(df['value'])  # Trace le calcul
median = np.median(df['value'])  # Trace le calcul
```

## Métriques Automatiques Capturées

### Métriques Système

- `system.cpu.usage`: Utilisation CPU (%)
- `system.memory.usage`: Utilisation mémoire (bytes)
- `system.gc.count`: Nombre de collections du GC
- `system.gc.duration`: Durée des collections du GC (ms)

### Métriques de Données

- `data.raw.rows`: Nombre total de lignes brutes traitées
- `data.processed.rows`: Nombre total de lignes traitées
- `data.filtered.rows`: Nombre total de lignes filtrées
- `data.processing.time`: Temps de traitement (ms)
- `data.size`: Taille des données traitées (bytes)

## Attributs de Span pour les Opérations de Données

### Pandas

- `pandas.rows`: Nombre de lignes dans un DataFrame
- `pandas.columns`: Nombre de colonnes
- `pandas.memory_bytes`: Taille mémoire estimée
- `pandas.input_rows`: Lignes en entrée d'une opération
- `pandas.output_rows`: Lignes en sortie
- `pandas.filtered_rows`: Lignes filtrées
- `processing_time_ms`: Temps de traitement

### NumPy

- `numpy.input_size`: Taille des données d'entrée
- `processing_time_ms`: Temps de traitement

## Exportation des Données d'Observabilité

### Prometheus (Métriques)

Les métriques sont automatiquement exposées sur un endpoint HTTP (par défaut: port 8000)
```
http://localhost:8000/metrics
```

### OpenTelemetry (Traces)

Les traces peuvent être envoyées à un collecteur OpenTelemetry:
```python
client = auto_instrument(
    service_name="mon-app",
    otlp_endpoint="http://collector:4317"
)
```

### Console (Développement)

En environnement de développement, les données sont également affichées dans la console.

## Exemples d'Utilisations Avancées

### ETL Pipeline

```python
def etl_pipeline():
    # Extraction
    data = extract_data()
    
    # Transformation
    processed_data = transform_data(data)
    
    # Chargement
    load_data(processed_data)
```

Toutes les étapes sont automatiquement tracées avec:
- Nombre de lignes à chaque étape
- Temps de traitement
- Taille des données
- Logs structurés JSON
- Métriques de performance

### API Web

```python
from flask import Flask, request
from autotelemetry import auto_instrument

app = Flask(__name__)
client = auto_instrument(service_name="api-service")
logger = client.get_logger()
request_counter = client.create_counter("api.requests.count", "Nombre de requêtes API", "1")

@app.route("/api/data")
def get_data():
    request_counter.add(1, {"endpoint": "/api/data"})
    logger.info("Requête reçue", extra={"data": {"query_params": dict(request.args)}})
    
    # Logique de récupération des données...
    
    return {"data": [...], "status": "success"}
```

## Bonnes Pratiques

1. **Utilisez des noms standardisés**: Suivez le pattern `domaine.entité.action` pour les métriques
2. **Spécifiez les unités**: Toujours préciser l'unité pour les métriques (`ms`, `bytes`, `1` pour les compteurs)
3. **Logs structurés**: Utilisez toujours `extra={"data": {...}}` pour les données structurées
4. **Gérez les erreurs**: Les exceptions sont automatiquement tracées, mais ajoutez du contexte quand c'est possible
5. **Métriques ciblées**: Créez des métriques pour des KPIs business spécifiques

## Dépannage

### Problèmes Courants

1. **Boucles d'instrumentation**: Si vous observez des erreurs de récursion, utilisez `SimpleObservabilityClient` au lieu de `auto_instrument`
2. **Ports utilisés**: Prometheus nécessite un port disponible, changez avec `prometheus_port`
3. **Trop de données**: Filtrez les modules à instrumenter pour les grandes applications

### Astuces de Performance

- Désactivez l'export console en production: `enable_console_export=False`
- Limitez l'auto-instrumentation aux modules critiques
- Utilisez des agrégations côté serveur pour les métriques à haute cardinalité

## Ressources

- **Prometheus**: Pour visualiser les métriques (compatible avec Grafana)
- **Jaeger/Zipkin**: Pour explorer les traces distribuées
- **Kibana/Elasticsearch**: Pour rechercher dans les logs JSON structurés

## Conclusion

AutoTelemetry transforme l'observabilité en Python d'une tâche complexe en une solution simple activable en une ligne de code. Elle est particulièrement puissante pour les applications de traitement de données, offrant une visibilité automatique sur les volumes de données et les performances à chaque étape du traitement. 