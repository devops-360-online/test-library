# Simple Observability

Bibliothèque d'auto-instrumentation pour standardiser les métriques, logs et traces avec une seule ligne de code.

## Installation

```bash
pip install simple_observability
```

## Utilisation

L'utilisation est extrêmement simple - ajoutez seulement une ligne à votre code :

```python
# Une seule ligne pour activer toute l'observabilité
from simple_observability import auto_instrument
auto_instrument(service_name="mon-service")

# Votre code existant reste inchangé et est automatiquement instrumenté
def process_data(df):
    # Les métriques, logs et traces sont automatiquement collectés
    result = df.groupby('category').sum()
    return result
```

## Fonctionnalités

La bibliothèque va automatiquement :

- **Tracer toutes les fonctions** sans décorateurs supplémentaires
- **Collecter les métriques système** (CPU, mémoire, GC)
- **Structurer les logs** avec contexte de trace
- **Instrumenter les bibliothèques de data science** (Pandas, NumPy, etc.)
- **Exporter les données** vers Prometheus, OpenTelemetry Collector, ou la console

## Configuration

Par défaut, auto_instrument() détecte l'environnement et configure tout automatiquement. Pour personnaliser :

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

Ou via variables d'environnement :

```bash
export SERVICE_NAME="mon-service"
export SERVICE_VERSION="1.0.0"
export ENVIRONMENT="production"
export PROMETHEUS_PORT="8000"
export OTLP_ENDPOINT="http://otel-collector:4317"
export LOG_LEVEL="INFO"
export JSON_LOGS="true"
```

## Avantages 

1. **Simplicité maximale** : Une seule ligne pour activer toute l'observabilité
2. **Standardisation** : Toutes les applications suivent les mêmes pratiques
3. **Productivité** : Réduction du temps de développement consacré à l'observabilité
4. **Facilité de maintenance** : Centralisation des standards
5. **Visibilité améliorée** : Dashboards et alertes cohérents

## Exemple Complet

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

## Architecture

La bibliothèque utilise OpenTelemetry comme fondation pour générer et exporter les signaux d'observabilité.
Elle ajoute une couche d'auto-instrumentation qui analyse votre code et y injecte des traces, 
métriques et logs de manière transparente, sans nécessiter de modifications de votre code existant. 