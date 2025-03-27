# Guide de Démarrage Rapide

Ce guide vous montre comment intégrer `simple_observability` dans votre application Python de traitement de données.

## Installation

Installez la bibliothèque via pip :

```bash
pip install simple_observability
```

## Utilisation basique

### Auto-instrumentation

```python
# Une seule ligne pour activer toute l'observabilité
from simple_observability import auto_instrument
auto_instrument(service_name="mon-service")

# Votre code existant est automatiquement instrumenté
def process_data(df):
    # Les métriques, logs et traces sont automatiquement collectés
    result = df.groupby('category').sum()
    return result
```

### Configuration avancée (optionnelle)

Si vous souhaitez personnaliser le comportement de l'auto-instrumentation :

```python
auto_instrument(
    service_name="mon-service",
    service_version="1.0.0",
    environment="production",  # ou "development", "testing", "staging"
    prometheus_port=8000,      # port pour exposer les métriques
    otlp_endpoint="http://otel-collector:4317",  # pour envoyer les données à un collecteur
    json_logs=True,            # format JSON pour les logs en production
    enable_console_export=True # exporter vers la console en développement
)
```

### Fonctionnalités automatiques

L'auto-instrumentation va automatiquement :

1. **Tracer toutes les fonctions** :
   - Création de spans pour chaque appel de fonction
   - Mesure des durées d'exécution
   - Propagation du contexte entre les appels

2. **Collecter les métriques** :
   - Métriques système (CPU, mémoire, etc.)
   - Métriques applicatives (nombre d'appels, durées, etc.)
   - Métriques de traitement de données (lignes traitées, erreurs, etc.)

3. **Logger les informations** :
   - Logs structurés en JSON
   - Contexte de trace inclus
   - Niveaux de log appropriés

4. **Mesurer les performances** :
   - Temps d'exécution des fonctions
   - Utilisation des ressources
   - Points chauds de performance

5. **Détecter les anomalies** :
   - Erreurs et exceptions
   - Performances anormales
   - Utilisation excessive des ressources

### Exemple complet

```python
import pandas as pd
from simple_observability import auto_instrument

# Activer l'auto-instrumentation
auto_instrument(service_name="data-pipeline")

def load_data():
    # Les métriques, logs et traces sont automatiquement collectés
    df = pd.read_csv("data.csv")
    return df

def transform_data(df):
    # Les performances et métriques sont automatiquement mesurés
    df['total'] = df['value1'] + df['value2']
    return df

def save_data(df):
    # Les erreurs sont automatiquement détectées et tracées
    df.to_csv("output.csv")

def main():
    try:
        # Chaque étape est automatiquement tracée
        df = load_data()
        df_transformed = transform_data(df)
        save_data(df_transformed)
    except Exception as e:
        # Les erreurs sont automatiquement loggées avec contexte
        raise

if __name__ == "__main__":
    main()
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