# Référence de l'API

Ce document décrit l'API fournie par la bibliothèque `autotelemetry`.

## Fonction principale

### auto_instrument

La fonction principale et la seule que vous aurez besoin d'appeler dans la plupart des cas:

```python
auto_instrument(
    service_name: str,
    service_version: Optional[str] = None,
    environment: Optional[str] = None,
    prometheus_port: Optional[int] = None,
    log_level: Optional[int] = None,
    additional_attributes: Optional[Dict[str, str]] = None,
    otlp_endpoint: Optional[str] = None,
    enable_console_export: Optional[bool] = None,
    json_logs: Optional[bool] = True,  # Toujours True en production
    auto_shutdown: bool = True,
) -> SimpleObservabilityClient
```

Active automatiquement toutes les fonctionnalités d'observabilité avec une seule ligne, y compris:
- L'instrumentation automatique des fonctions
- La configuration des logs structurés en JSON (obligatoire)
- La configuration des métriques avec Prometheus
- La configuration des traces
- La configuration des exportateurs

#### Paramètres

- **service_name** (str): Nom du service (obligatoire)
- **service_version** (str, optionnel): Version du service
- **environment** (str, optionnel): Environnement d'exécution (development, test, staging, production)
- **prometheus_port** (int, optionnel): Port pour exposer les métriques Prometheus
- **log_level** (int, optionnel): Niveau de log (valeurs de logging.DEBUG, logging.INFO, etc.)
- **additional_attributes** (dict, optionnel): Attributs supplémentaires à ajouter à tous les signaux
- **otlp_endpoint** (str, optionnel): Endpoint OTLP pour envoyer les données de télémétrie
- **enable_console_export** (bool, optionnel): Activer l'export vers la console
- **json_logs** (bool, optionnel): Format JSON pour les logs. Par défaut à True et obligatoire en production
- **auto_shutdown** (bool, optionnel): Enregistrer automatiquement la fermeture propre

#### Retour

- **SimpleObservabilityClient**: Instance du client d'observabilité

#### Exemple

```python
from autotelemetry import auto_instrument

# Configuration minimale
auto_instrument(service_name="mon-service")

# Configuration complète
client = auto_instrument(
    service_name="mon-service",
    service_version="1.0.0",
    environment="production",
    prometheus_port=8000,
    log_level=logging.INFO,
    additional_attributes={"team": "data-engineering"},
    otlp_endpoint="http://otel-collector:4317",
    enable_console_export=False,
    json_logs=True  # Obligatoire en production
)
```

## Classes et constantes utilitaires

### LogLevel

Constantes pour les niveaux de log:

```python
LogLevel.DEBUG    # = logging.DEBUG
LogLevel.INFO     # = logging.INFO
LogLevel.WARNING  # = logging.WARNING
LogLevel.ERROR    # = logging.ERROR
LogLevel.CRITICAL # = logging.CRITICAL
```

### Environment

Constantes pour les environnements standard:

```python
Environment.DEVELOPMENT  # = "development"
Environment.TEST         # = "test"
Environment.STAGING      # = "staging"
Environment.PRODUCTION   # = "production"
```

## Client d'observabilité

Dans la plupart des cas, vous n'aurez pas besoin d'interagir directement avec le client d'observabilité, car l'auto-instrumentation s'occupe de tout. Cependant, la fonction `auto_instrument` renvoie une instance de `SimpleObservabilityClient` que vous pouvez utiliser pour des cas avancés.

### SimpleObservabilityClient

Le client unifié pour l'observabilité.

#### Méthodes

- **get_logger(name=None)**: Obtient un logger configuré avec format JSON
- **create_counter(name, description=None, unit=None)**: Crée un compteur
- **create_histogram(name, description=None, unit=None)**: Crée un histogramme
- **create_system_metrics()**: Crée des métriques système standard
- **start_system_metrics_collection(metrics)**: Démarre la collecte périodique des métriques système
- **shutdown()**: Arrête proprement le client d'observabilité

#### Exemple d'utilisation avancée

```python
from autotelemetry import auto_instrument

# Obtenir le client
client = auto_instrument(service_name="mon-service")

# Obtenir un logger pour un usage spécial
logger = client.get_logger("mon_module")
logger.info("Message personnalisé")  # Sera automatiquement formaté en JSON

# Créer une métrique personnalisée
counter = client.create_counter(
    name="custom_requests_total",
    description="Nombre total de requêtes personnalisées",
    unit="1"
)
counter.add(1, {"endpoint": "/api/special"})

# Arrêt manuel (généralement pas nécessaire)
# client.shutdown()
```

## Logger personnalisé

Le logger fourni par `SimpleObservabilityClient.get_logger()` est une extension du logger standard Python avec des fonctionnalités supplémentaires pour la journalisation de données structurées en JSON.

### DataLogger

#### Méthodes spécifiques

- **with_data(\*\*kwargs)**: Retourne un context manager qui ajoute des données au contexte actuel
- **data(level, msg, data=None, \*args, \*\*kwargs)**: Log un message avec des données structurées

#### Exemple de logging JSON standardisé

```python
# Obtenir un logger
logger = client.get_logger()

# Logging simple (automatiquement formaté en JSON)
logger.info("Message simple")

# Logging avec contexte enrichi
with logger.with_data(job_id="12345", batch_id="abc"):
    logger.info("Traitement du lot")
    
    # Logging de données structurées
    logger.data(
        level=logging.INFO,
        msg="Statistiques de traitement",
        data={
            "rows_processed": 1000,
            "duration_ms": 1200
        }
    )
```

Résultat du format JSON:

```json
{
  "timestamp": "2023-06-15T14:32:45.123Z",
  "level": "INFO",
  "logger": "mon_module",
  "message": "Statistiques de traitement",
  "service.name": "mon-service",
  "service.version": "1.0.0",
  "deployment.environment": "production",
  "trace_id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "span_id": "b2c3d4e5f6g7h8i9",
  "data": {
    "job_id": "12345",
    "batch_id": "abc",
    "rows_processed": 1000,
    "duration_ms": 1200
  }
}
```

## Auto-instrumentation interne

Ces fonctions sont utilisées en interne par `auto_instrument()` et ne sont généralement pas appelées directement:

- **_function_decorator(func)**: Décorateur qui trace automatiquement les fonctions
- **_apply_auto_instrumentation()**: Applique l'auto-instrumentation en modifiant le mécanisme d'import
- **_instrument_module(module)**: Instrumente un module existant
- **_setup_system_metrics()**: Configure les métriques système automatiques
- **_setup_data_science_instrumentation()**: Ajoute une instrumentation spécifique pour les bibliothèques de data science 