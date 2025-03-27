# AutoTelemetry 📊

Une bibliothèque simplifiée d'observabilité pour Python avec auto-instrumentation pour métriques, logs et traces.

## Pourquoi cette bibliothèque ?

### Le problème

L'observabilité moderne repose sur trois piliers fondamentaux : les métriques, les logs et les traces distribuées. Cependant, l'implémentation de ces trois composants présente plusieurs défis :

1. **Complexité technique** : OpenTelemetry est puissant mais complexe, avec des APIs distinctes pour chaque pilier.
2. **Code répétitif** : Les développeurs écrivent le même code d'initialisation dans chaque application.
3. **Inconsistance** : Sans standards, chaque équipe implémente différemment les noms de métriques, formats de logs, etc.
4. **Courbe d'apprentissage** : Les développeurs doivent comprendre OpenTelemetry avant de pouvoir instrumenter leurs applications.
5. **Fragmentation** : De nombreuses bibliothèques tierces à intégrer et maintenir.

### Notre solution

`autotelemetry` est une bibliothèque d'auto-instrumentation qui :

- **Auto-instrumente** automatiquement votre code avec une seule ligne
- **Standardise** les noms, formats et attributs à l'échelle de l'organisation
- **Impose le format JSON** pour tous les logs, garantissant une structure cohérente et exploitable
- **Réduit le code d'initialisation** à une seule ligne
- **Adapte automatiquement** son comportement selon l'environnement (dev, test, prod)
- **Spécialise les abstractions** pour les opérations de traitement de données

## Auto-instrumentation

Notre bibliothèque permet une auto-instrumentation avec un minimum d'effort :

```python
# Une seule ligne pour activer toute l'observabilité
from autotelemetry import auto_instrument
auto_instrument(service_name="mon-service")

# Votre code existant est automatiquement instrumenté
def process_data(df):
    # Les métriques, logs et traces sont automatiquement collectés
    result = df.groupby('category').sum()
    return result
```

La bibliothèque va automatiquement :
- Tracer toutes les fonctions
- Collecter les métriques système et applicatives
- Logger les informations pertinentes en format JSON standardisé
- Mesurer les performances
- Détecter les anomalies

## Avantages pour les équipes

1. **Simplicité maximale** : Une seule ligne pour activer toute l'observabilité
2. **Standardisation** : Toutes les applications suivent les mêmes pratiques d'observabilité
3. **Productivité** : Réduction du temps de développement consacré à l'observabilité
4. **Facilité de maintenance** : Centralisation des standards et mises à jour
5. **Visibilité améliorée** : Dashboards et alertes cohérents grâce aux standards
6. **Logs JSON obligatoires** : Format structuré pour une meilleure analyse et recherche

## Prérequis

### Dépendances Python

```
Python >= 3.8
opentelemetry-api >= 1.18.0
opentelemetry-sdk >= 1.18.0
opentelemetry-exporter-otlp >= 1.18.0
opentelemetry-exporter-prometheus >= 1.18.0
prometheus-client >= 0.16.0
psutil >= 5.9.0
```

### Infrastructure (optionnelle)

Pour exploiter pleinement cette bibliothèque en production :

- **Prometheus** : Pour stocker et interroger les métriques
- **Grafana** : Pour visualiser les métriques
- **OpenTelemetry Collector** : Pour recevoir et router les données de télémétrie
- **Jaeger ou Zipkin** : Pour visualiser les traces distribuées
- **Elasticsearch** : Pour stocker et interroger les logs JSON

## Installation

```bash
pip install autotelemetry
```

## Utilisation simple

```python
from autotelemetry import auto_instrument, LogLevel, Environment

# Une seule ligne active toute l'observabilité
client = auto_instrument(
    service_name="mon-service",
    environment=Environment.PRODUCTION,  # Les logs JSON sont obligatoires en production
    log_level=LogLevel.INFO
)

# Le reste de votre code est automatiquement instrumenté
def process_data():
    # Cette fonction est automatiquement tracée
    # Des logs structurés et des métriques sont générés
    pass
```

## Fonctionnalités

- **Auto-instrumentation**: Injecte automatiquement le traçage dans toutes les fonctions
- **Logs JSON**: Format obligatoire en production pour une analyse efficace
- **Métriques**: Collecte automatique des métriques système et applicatives
- **Traces**: Propagation automatique du contexte de trace
- **Standards intégrés**: Conventions de nommage et d'attributs OpenTelemetry

## Configuration

```python
client = auto_instrument(
    service_name="mon-service",          # Obligatoire: Nom du service
    service_version="1.0.0",             # Optionnel: Version du service
    environment=Environment.PRODUCTION,  # Environnement (PRODUCTION = logs JSON obligatoires)
    prometheus_port=8000,                # Port pour les métriques Prometheus
    log_level=LogLevel.INFO,             # Niveau de log
    additional_attributes={"team": "data"}, # Attributs supplémentaires
    otlp_endpoint="localhost:4317",      # Endpoint OTLP
    json_logs=True,                      # JSON logs (toujours True en production)
)
```

## Exemple complet

```python
import pandas as pd
import time
from autotelemetry import auto_instrument, LogLevel, Environment

# Initialisation
client = auto_instrument("demo-service", environment=Environment.PRODUCTION)
logger = client.get_logger()

# Fonctions de traitement de données (auto-instrumentées)
def load_data():
    logger.info("Chargement des données")
    # Les données sont automatiquement tracées
    return pd.DataFrame({"valeur": range(100)})

def process_data(df):
    # Les métriques sont collectées automatiquement
    logger.info("Traitement des données", 
                data={"rows": len(df), "mean": df["valeur"].mean()})
    return df[df["valeur"] > 50]

# Utilisation
try:
    data = load_data()
    result = process_data(data)
    logger.info("Traitement terminé", 
                data={"rows_processed": len(result)})
except Exception as e:
    logger.error(f"Erreur: {str(e)}")
finally:
    # Arrêt propre (optionnel, fait automatiquement en fin de programme)
    client.shutdown()
```

## Format des logs JSON

Tous les logs sont automatiquement structurés en JSON avec les champs suivants:

```json
{
  "timestamp": "2023-08-15T10:23:45.123Z",
  "level": "INFO",
  "logger": "mon_module",
  "message": "Traitement terminé",
  "service.name": "mon-service",
  "service.version": "1.0.0",
  "deployment.environment": "production",
  "trace_id": "a1b2c3d4e5f6...",
  "span_id": "a1b2c3d4e5f6...",
  "data": {
    "rows_processed": 150,
    "processing_time_ms": 45.2,
    "memory_usage_mb": 128.5
  }
}
```

## Architecture

AutoTelemetry utilise OpenTelemetry comme fondation pour les signaux d'observabilité. La bibliothèque simplifie grandement son utilisation en injectant automatiquement:

- Des métriques standardisées
- Des logs JSON structurés (obligatoires en production)
- Des traces distribuées avec propagation de contexte

## Documentation

Pour plus de détails sur l'utilisation et les fonctionnalités :

- [Guide de démarrage rapide](docs/quickstart.md)
- [Concepts fondamentaux](docs/concepts.md)
- [API de référence](docs/api.md)
- [Exemples](examples/)

## Contribuer

Les contributions sont les bienvenues ! Consultez notre [guide de contribution](CONTRIBUTING.md) pour commencer.

## Licence

MIT 