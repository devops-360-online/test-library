# Référence API

## ObservabilityClient

Classe principale qui fournit l'accès à toutes les fonctionnalités d'observabilité.

```python
ObservabilityClient(
    service_name: str,
    service_version: Optional[str] = None,
    environment: Optional[str] = None,
    prometheus_port: Optional[int] = None,
    log_level: Optional[int] = None,
    additional_attributes: Optional[Dict[str, Any]] = None,
    otlp_endpoint: Optional[str] = None,
    enable_console_export: Optional[bool] = None,
    json_logs: Optional[bool] = None,
    auto_shutdown: bool = True
)
```

### Paramètres

- `service_name`: Nom du service/application
- `service_version`: Version du service (défaut: depuis env ou "0.1.0")
- `environment`: Environnement de déploiement (défaut: depuis env ou "development")
- `prometheus_port`: Port pour exposer les métriques Prometheus (défaut: 8000)
- `log_level`: Niveau de log (défaut: INFO)
- `additional_attributes`: Attributs additionnels à inclure dans toute la télémétrie
- `otlp_endpoint`: Endpoint du collecteur OpenTelemetry (optionnel)
- `enable_console_export`: Activer l'export console pour développement (défaut: auto)
- `json_logs`: Utiliser le format JSON pour les logs (défaut: auto selon env)
- `auto_shutdown`: Enregistrer un gestionnaire d'arrêt automatique (défaut: True)

### Méthodes principales

#### Métriques

```python
def create_counter(
    name: str, 
    description: str, 
    unit: str = "1",
    attributes: Optional[Dict[str, str]] = None
) -> Any
```

Crée un compteur (valeur croissante uniquement).

```python
def create_gauge(
    name: str, 
    description: str, 
    unit: str = "1",
    attributes: Optional[Dict[str, str]] = None
) -> Any
```

Crée une jauge (valeur qui peut augmenter ou diminuer).

```python
def create_histogram(
    name: str, 
    description: str, 
    unit: str = "1",
    attributes: Optional[Dict[str, str]] = None
) -> Any
```

Crée un histogramme (distribution de valeurs).

```python
def create_data_processing_metrics(
    prefix: str = "data"
) -> Dict[str, Any]
```

Crée un ensemble standard de métriques pour le traitement de données:
- `rows_processed`: Compteur de lignes traitées
- `processing_errors`: Compteur d'erreurs
- `processing_duration`: Histogramme des durées
- `batch_size`: Histogramme des tailles de lot
- `memory_usage`: Jauge de l'utilisation mémoire

#### Traces

```python
def get_tracer(name: Optional[str] = None) -> Tracer
```

Obtient un traceur pour la création de spans.

```python
def start_span(
    name: str, 
    attributes: Optional[Dict[str, Any]] = None
) -> Span
```

Démarre une nouvelle span.

```python
@contextmanager
def span(
    name: str, 
    attributes: Optional[Dict[str, Any]] = None
) -> ContextManager[Span]
```

Gestionnaire de contexte pour créer une span.

```python
def trace_function(
    name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None
) -> Callable[[F], F]
```

Décorateur pour tracer une fonction.

```python
def trace_data_processing(
    name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None
) -> Callable[[F], F]
```

Décorateur spécialisé pour les fonctions de traitement de données.

```python
def data_operation(
    operation_type: str, 
    target: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None
) -> ContextManager[Span]
```

Gestionnaire de contexte pour une opération de données standardisée.

#### Logs

```python
def get_logger(name: Optional[str] = None) -> DataLogger
```

Obtient un logger configuré.

#### Utilitaires

```python
@contextmanager
def timed_span(
    name: str, 
    attributes: Optional[Dict[str, Any]] = None,
    histogram: Optional[Any] = None
) -> ContextManager[Span]
```

Gestionnaire de contexte qui crée une span et enregistre sa durée dans un histogramme.

```python
@contextmanager
def timed_task(
    task_name: str, 
    attributes: Optional[Dict[str, Any]] = None
) -> ContextManager[Dict[str, Any]]
```

Gestionnaire de contexte de haut niveau pour chronométrer une tâche avec métriques et traces.

```python
def shutdown() -> None
```

Arrête proprement tous les composants de télémétrie.

## DataLogger

Extension du logger Python standard avec fonctionnalités de données structurées.

```python
def with_data(**kwargs) -> DataLoggingContext
```

Crée un contexte de logging avec attributs de données.

```python
def data(
    level, 
    msg, 
    *args, 
    data: Dict[str, Any] = {}, 
    **kwargs
)
```

Enregistre un message avec données structurées.

## Standards

Les constantes et utilitaires de standardisation sont accessibles via:

```python
from simple_observability.standards import (
    AttributeNames,      # Noms d'attributs standards
    Environment,         # Environnements standards
    LogFormat,           # Formats de log standards
    LogLevel,            # Niveaux de log standards
    MetricNames,         # Noms de métriques standards
    SpanNames            # Noms de spans standards
)
```

### AttributeNames

Noms standards pour les attributs de télémétrie:

```python
AttributeNames.SERVICE_NAME       # "service.name"
AttributeNames.SERVICE_VERSION    # "service.version"
AttributeNames.ENVIRONMENT        # "deployment.environment"
AttributeNames.DATA_SOURCE        # "data.source"
AttributeNames.DATA_OPERATION     # "data.operation" 
# ... etc.
```

### Environment

Valeurs standards d'environnement:

```python
Environment.DEVELOPMENT.value  # "development"
Environment.TESTING.value      # "testing"
Environment.STAGING.value      # "staging"
Environment.PRODUCTION.value   # "production"
```

### SpanNames

Noms standards d'opérations de span:

```python
SpanNames.DATA_LOAD        # "data.load"
SpanNames.DATA_TRANSFORM   # "data.transform"
SpanNames.DATA_CLEAN       # "data.clean"
# ... etc.
``` 