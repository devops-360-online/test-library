# Explication des Sorties des Exemples AutoTelemetry

Ce document explique les sorties générées par les trois exemples d'AutoTelemetry.

## 1. Simple Example (`simple_example.py`)

```
2025-03-27 11:10:35.572 - autotelemetry.autotelemetry - INFO - Observabilité initialisée pour exemple-simple
2025-03-27 11:10:35.572 - __main__ - INFO - Démarrage de l'exemple AutoTelemetry
2025-03-27 11:10:35.572 - __main__ - INFO - Génération de 1046 lignes de données
2025-03-27 11:10:35.581 - __main__ - INFO - Données générées avec succès
2025-03-27 11:10:35.581 - __main__ - WARNING - Opération susceptible d'échouer
2025-03-27 11:10:35.581 - __main__ - ERROR - Erreur dans l'exécution: Erreur simulée pour la démonstration
2025-03-27 11:10:35.581 - __main__ - INFO - Arrêt de l'exemple
2025-03-27 11:10:35.581 - autotelemetry.autotelemetry - INFO - Arrêt propre de l'observabilité
2025-03-27 11:10:35.581 - autotelemetry.autotelemetry - INFO - Arrêt propre de l'observabilité
2025-03-27 11:10:35.581 - opentelemetry.sdk.metrics._internal - WARNING - shutdown can only be called once
```

### Explication:

1. **Initialisation**: Le client d'observabilité est initialisé pour le service "exemple-simple".
2. **Démarrage**: L'exemple démarre et le logger enregistre cet événement.
3. **Génération de données**: L'exemple génère un ensemble aléatoire de 1046 lignes de données.
4. **Succès de génération**: Les données sont générées avec succès (avec les métadonnées en JSON, non visibles dans la sortie texte).
5. **Avertissement**: L'exemple génère un avertissement avant de simuler une erreur (la fonction `simulate_error` a une chance de 30% d'échouer).
6. **Erreur simulée**: Une erreur est déclenchée intentionnellement pour démontrer la gestion des erreurs.
7. **Arrêt**: L'exemple se termine et le client d'observabilité effectue un arrêt propre.
8. **Avertissement shutdown**: Un avertissement indique que la méthode `shutdown()` a été appelée deux fois (une fois explicitement et une fois par le gestionnaire `atexit`).

La sortie montre comment l'exemple gère le cycle de vie complet: initialisation, logs informatifs, avertissements et erreurs. Notez que le traitement des données n'a pas eu lieu car une erreur a été simulée avant d'atteindre cette étape.

## 2. Advanced Configuration (`advanced_configuration.py`)

```
2025-03-27 11:11:16.176 - autotelemetry.autotelemetry - INFO - Observabilité initialisée pour demo-advanced
2025-03-27 11:11:16.176 - __main__ - INFO - Démarrage du pipeline de données
2025-03-27 11:11:16.682 - __main__ - INFO - Données extraites: 100 lignes
2025-03-27 11:11:17.390 - __main__ - INFO - Données transformées: 93 lignes
2025-03-27 11:11:17.700 - __main__ - INFO - Données chargées avec succès
2025-03-27 11:11:17.700 - __main__ - INFO - Pipeline terminé avec succès
Pipeline exécuté avec succès
2025-03-27 11:11:17.700 - autotelemetry.autotelemetry - INFO - Arrêt propre de l'observabilité
2025-03-27 11:11:17.701 - autotelemetry.autotelemetry - INFO - Arrêt propre de l'observabilité
2025-03-27 11:11:17.701 - opentelemetry.sdk.metrics._internal - WARNING - shutdown can only be called once
```

### Explication:

1. **Initialisation**: Le client d'observabilité est initialisé pour le service "demo-advanced" avec une configuration personnalisée.
2. **Démarrage du pipeline**: Le pipeline de traitement de données démarre.
3. **Extraction**: 100 lignes de données sont extraites, avec un délai simulé de 0,5 seconde.
4. **Transformation**: Les données sont transformées, avec un délai simulé de 0,7 seconde. Notez que 7 lignes ont été filtrées comme valeurs aberrantes (100 → 93).
5. **Chargement**: Les données transformées sont chargées, avec un délai simulé de 0,3 seconde.
6. **Finalisation**: Le pipeline se termine avec succès et affiche "Pipeline exécuté avec succès".
7. **Arrêt**: Comme dans l'exemple précédent, il y a deux appels à la méthode d'arrêt.

Cet exemple montre comment AutoTelemetry peut être utilisé pour suivre un pipeline ETL complet (Extract-Transform-Load) avec des logs informatifs à chaque étape et des attributs personnalisés.

## 3. Auto Instrument Example (`auto_instrument_example.py`)

```
2025-03-27 11:13:20.584 - autotelemetry.autotelemetry - INFO - Observabilité initialisée pour demo-auto-instrument
2025-03-27 11:13:20.584 - __main__ - INFO - Démarrage du traitement
Génération des données...
2025-03-27 11:13:20.584 - __main__ - INFO - Génération de 1000 lignes de données
2025-03-27 11:13:20.586 - __main__ - INFO - Données générées avec succès
Données générées : 1000 lignes
Traitement des données...
2025-03-27 11:13:20.587 - __main__ - INFO - Données traitées
Données traitées : 507 lignes
Statistiques par catégorie :
          valeur                        
           count       mean          sum
categorie                               
A            169  23.709946  4006.980949
B            170  24.842728  4223.263742
C            168  26.214799  4404.086293
2025-03-27 11:13:20.589 - __main__ - INFO - Traitement terminé avec succès
2025-03-27 11:13:20.590 - autotelemetry.autotelemetry - INFO - Arrêt propre de l'observabilité
{
    "name": "process_data",
    "context": {
        "trace_id": "0x7bc8ae831498c4da81711ec6967f55d3",
        "span_id": "0x595929d73dbd3ab4",
        "trace_state": "[]"
    },
    "kind": "SpanKind.INTERNAL",
    "parent_id": null,
    "start_time": "2025-03-27T10:13:20.586521Z",
    "end_time": "2025-03-27T10:13:20.587561Z",
    "status": {
        "status_code": "UNSET"
    },
    "attributes": {},
    "events": [],
    "links": [],
    "resource": {
        "attributes": {
            "telemetry.sdk.language": "python",
            "telemetry.sdk.name": "opentelemetry",
            "telemetry.sdk.version": "1.31.1",
            "service.name": "demo-auto-instrument",
            "service.version": "1.0.0",
            "deployment.environment": "development"
        },
        "schema_url": ""
    }
}
2025-03-27 11:13:20.590 - autotelemetry.autotelemetry - INFO - Arrêt propre de l'observabilité
2025-03-27 11:13:20.590 - opentelemetry.sdk.metrics._internal - WARNING - shutdown can only be called once
```

### Explication:

1. **Initialisation**: Le client est initialisé pour "demo-auto-instrument".
2. **Génération de données**: 1000 lignes de données sont générées avec des valeurs aléatoires.
3. **Traitement des données**: 
   - Les données sont filtrées (valeurs <= 50) ce qui donne 507 lignes sur 1000.
   - Les données sont groupées par catégorie (A, B, C).
   - Un span de trace est créé pour la fonction `process_data`.
4. **Résultats**: 
   - Affichage des statistiques par catégorie (nombre, moyenne, somme).
   - Catégorie A: 169 lignes avec une moyenne d'environ 23,7.
   - Catégorie B: 170 lignes avec une moyenne d'environ 24,8.
   - Catégorie C: 168 lignes avec une moyenne d'environ 26,2.
5. **Trace OpenTelemetry**: L'exemple affiche les détails d'une trace OpenTelemetry pour la fonction `process_data`. Cette trace contient:
   - Un identifiant de trace et d'intervalle (span)
   - Les horodatages de début et de fin
   - Les attributs de ressource, y compris le nom et la version du service

Cet exemple illustre comment AutoTelemetry peut être utilisé pour tracer des fonctions spécifiques et comment les traces sont structurées dans OpenTelemetry.

## Nouvelles Métriques de Données Collectées Automatiquement

La bibliothèque AutoTelemetry capture maintenant automatiquement des métriques clés sur les données traitées, sans avoir besoin d'ajouter des statistiques complexes comme la médiane dans les métriques. Voici les métriques principales qui sont collectées:

### Métriques de Volume de Données

- **data.raw.rows**: Compteur du nombre total de lignes de données brutes traitées.
- **data.processed.rows**: Compteur du nombre total de lignes de données traitées après les différentes étapes.
- **data.filtered.rows**: Compteur du nombre total de lignes filtrées/supprimées.
- **data.size**: Histogramme de la taille des données en octets.

### Métriques de Performance

- **data.processing.time**: Histogramme du temps de traitement en millisecondes pour chaque opération.

### Attributs de Span pour les Opérations Pandas

Pour les opérations Pandas, chaque span de trace inclut désormais:

- Nombre de lignes en entrée (`pandas.input_rows`)
- Nombre de lignes en sortie (`pandas.output_rows`) 
- Nombre de lignes filtrées (`pandas.filtered_rows`)
- Taille mémoire estimée (`pandas.memory_bytes`)
- Temps de traitement (`processing_time_ms`)

### Attributs de Span pour les Opérations NumPy

Pour les opérations NumPy, chaque span de trace inclut:

- Taille des données d'entrée (`numpy.input_size`)
- Temps de traitement (`processing_time_ms`)

Ces métriques permettent de suivre de manière automatique et standardisée le flux des données à travers votre application, en se concentrant sur les volumes traités et les performances, sans surcharger avec des statistiques complexes.

## 4. Exemple d'Instrumentation des Données (`data_processing_example.py`)

```
[Exemple d'exécution]
2025-03-27 11:30:12.123 - autotelemetry.autotelemetry - INFO - Observabilité initialisée pour demo-data-metrics
2025-03-27 11:30:12.124 - __main__ - INFO - Démarrage de l'exemple d'instrumentation des données
2025-03-27 11:30:12.125 - __main__ - INFO - Génération d'un DataFrame de 50000 lignes et 8 colonnes
2025-03-27 11:30:12.987 - __main__ - INFO - DataFrame généré avec succès: 50000 lignes, 10 colonnes
2025-03-27 11:30:13.123 - __main__ - INFO - Mémoire utilisée par le DataFrame: 4.32 MB
2025-03-27 11:30:13.124 - __main__ - INFO - Filtrage des valeurs NaN...
2025-03-27 11:30:13.432 - __main__ - INFO - Après filtrage: 49243 lignes (supprimé 757 lignes)
2025-03-27 11:30:13.433 - __main__ - INFO - Calcul des statistiques de base...
2025-03-27 11:30:14.876 - __main__ - INFO - Groupement par catégorie...
2025-03-27 11:30:15.234 - __main__ - INFO - Filtrage des valeurs extrêmes...
2025-03-27 11:30:16.453 - __main__ - INFO - Après filtrage des valeurs extrêmes: 44987 lignes
2025-03-27 11:30:16.454 - __main__ - INFO - Préparation d'une jointure...
2025-03-27 11:30:16.455 - __main__ - INFO - Exécution de la jointure...
2025-03-27 11:30:16.789 - __main__ - INFO - Résultat final: 44987 lignes, 12 colonnes
2025-03-27 11:30:16.790 - __main__ - INFO - Traitement terminé en 4.67 secondes

Statistiques par catégorie:
------------------------------
[tableau de statistiques]

Résumé du traitement:
------------------------------
Lignes brutes: 50000
Lignes finales: 44987
Colonnes: 12
Temps de traitement: 4.67 secondes

2025-03-27 11:30:16.888 - __main__ - INFO - Exemple terminé. Consultez les métriques Prometheus sur le port 9093.
2025-03-27 11:30:16.889 - autotelemetry.autotelemetry - INFO - Arrêt propre de l'observabilité

{
    "name": "pandas.read_csv",
    "context": {
        "trace_id": "0x7bc8ae831498c4da81711ec6967f55d3",
        "span_id": "0x595929d73dbd3ab4",
        "trace_state": "[]"
    },
    "kind": "SpanKind.INTERNAL",
    "parent_id": null,
    "start_time": "2025-03-27T10:30:12.586521Z",
    "end_time": "2025-03-27T10:30:12.987561Z",
    "status": {
        "status_code": "UNSET"
    },
    "attributes": {
        "pandas.rows": 50000,
        "pandas.columns": 10,
        "pandas.memory_bytes": 4525600,
        "processing_time_ms": 401.04
    },
    "resource": {
        "attributes": {
            "telemetry.sdk.language": "python",
            "telemetry.sdk.name": "opentelemetry",
            "telemetry.sdk.version": "1.31.1",
            "service.name": "demo-data-metrics",
            "service.version": "1.0.0",
            "deployment.environment": "development"
        }
    }
}
```

### Explication:

Ce nouvel exemple montre l'instrumentation automatique des opérations de traitement de données:

1. **Génération de données**: Un grand DataFrame (50 000 lignes) est créé, et ses caractéristiques (nombre de lignes, colonnes, mémoire utilisée) sont automatiquement tracées.

2. **Opérations de traitement**:
   - Filtrage des valeurs manquantes (`dropna()`)
   - Calculs statistiques avec NumPy (`mean`, `median`, `std`, etc.)
   - Agrégation par catégorie avec Pandas (`groupby`)
   - Filtrage des valeurs extrêmes
   - Jointure de données (`merge`)

3. **Métriques automatiques**: Chaque opération génère automatiquement:
   - Des traces OpenTelemetry avec attributs détaillés
   - Des compteurs pour les lignes traitées, filtrées
   - Des histogrammes pour les temps de traitement
   - Des mesures de taille des données

4. **Trace détaillée**: L'exemple montre une trace pour l'opération de lecture, incluant:
   - Le nombre de lignes/colonnes
   - La taille mémoire en octets
   - Le temps de traitement précis

Cette approche permet de suivre automatiquement les volumes de données et les performances sans avoir à instrumenter manuellement chaque opération.

## Résumé des Fonctionnalités Démontrées

1. **Logs Structurés**: Tous les exemples montrent des logs structurés avec des niveaux de log appropriés.
2. **Métriques**: L'exemple simple montre comment créer et enregistrer des métriques personnalisées.
3. **Traces**: L'exemple auto-instrument montre comment créer des spans de trace pour des fonctions.
4. **Gestion des Erreurs**: L'exemple simple montre comment les erreurs sont capturées et tracées.
5. **Configuration Avancée**: L'exemple avancé montre comment personnaliser le client d'observabilité.
6. **Arrêt Propre**: Tous les exemples montrent l'arrêt propre du client d'observabilité.

AutoTelemetry simplifie considérablement l'instrumentation des applications Python en fournissant une API unifiée pour les logs, métriques et traces, tout en respectant les standards d'observabilité modernes comme OpenTelemetry et Prometheus.

# Architecture et Documentation de la Bibliothèque AutoTelemetry

## Structure de la Bibliothèque

La bibliothèque AutoTelemetry est organisée de façon modulaire pour faciliter l'instrumentation automatique des applications Python, avec un focus particulier sur les opérations de traitement de données.

```
autotelemetry/
├── __init__.py               # Exports des classes et fonctions principales
└── autotelemetry.py          # Code principal de la bibliothèque
```

## Composants Principaux

### 1. Client d'Observabilité (`SimpleObservabilityClient`)

C'est la classe principale qui coordonne tous les aspects de l'observabilité:

```python
client = SimpleObservabilityClient(
    service_name="mon-service",
    service_version="1.0.0",
    environment=Environment.PRODUCTION
)
```

**Méthodes principales**:

- `get_logger()`: Obtient un logger configuré
- `create_counter()`: Crée un compteur pour les métriques
- `create_histogram()`: Crée un histogramme pour les métriques
- `create_system_metrics()`: Configure des métriques système standards
- `start_system_metrics_collection()`: Démarre la collection des métriques système
- `shutdown()`: Arrête proprement tous les composants d'observabilité

### 2. Auto-Instrumentation (`auto_instrument`)

Fonction qui active automatiquement toutes les fonctionnalités d'observabilité:

```python
client = auto_instrument(
    service_name="mon-service",
    environment=Environment.PRODUCTION
)
```

**Aspects automatisés**:

- Instrumentation de toutes les fonctions existantes et futures
- Configuration des logs structurés en JSON
- Mise en place des exportateurs OpenTelemetry
- Instrumentation de bibliothèques comme Pandas et NumPy
- Métriques système automatiques

### 3. Logging Structuré (`DataLogger`)

Extension du logger Python standard avec support pour les données structurées:

```python
logger = client.get_logger()
logger.info("Message", extra={"data": {"key": "value"}})
```

**Fonctionnalités**:

- Formatage JSON automatique des logs
- Inclusion du contexte de trace dans chaque log
- Support pour les données structurées

### 4. Métriques de Données

Métriques automatiques pour les opérations de traitement de données:

- `data.raw.rows`: Lignes brutes traitées
- `data.processed.rows`: Lignes traitées après filtrage
- `data.filtered.rows`: Lignes filtrées
- `data.processing.time`: Temps de traitement
- `data.size`: Taille des données

## Documentation Détaillée des Classes et Méthodes

### `SimpleObservabilityClient`

**Constructeur**:

```python
def __init__(
    self,
    service_name: str,              # Nom du service (obligatoire)
    service_version: str = None,    # Version du service (par défaut: "1.0.0")
    environment: str = None,        # Environnement (dev/test/staging/prod)
    prometheus_port: int = None,    # Port pour Prometheus (par défaut: 8000)
    log_level: int = None,          # Niveau de log (par défaut: INFO)
    additional_attributes: dict = None,  # Attributs supplémentaires
    otlp_endpoint: str = None,      # Endpoint OTLP pour export
    enable_console_export: bool = None,  # Exporter dans la console
    json_logs: bool = None,         # Format JSON pour logs
    auto_shutdown: bool = True      # Arrêt automatique
)
```

**Méthodes clés**:

- `_setup_tracing()`: Configure le tracing OpenTelemetry
- `_setup_metrics()`: Configure les métriques OpenTelemetry
- `_setup_logging()`: Configure le logging standardisé

- `get_logger(name=None)`: Obtient un logger configuré pour le module spécifié

- `create_counter(name, description=None, unit=None, attributes=None)`: 
  Crée un compteur pour suivre des valeurs qui augmentent de manière monotone

- `create_histogram(name, description=None, unit=None, attributes=None)`: 
  Crée un histogramme pour suivre des distributions de valeurs

- `create_system_metrics()`: 
  Crée un ensemble standard de métriques système (CPU, mémoire, etc.)

- `start_system_metrics_collection(metrics)`: 
  Démarre la collecte périodique des métriques système

- `shutdown()`: 
  Arrête proprement tous les exportateurs et processeurs de télémétrie

### `auto_instrument`

```python
def auto_instrument(
    service_name: str,              # Nom du service (obligatoire)
    service_version: str = None,    # Version du service
    environment: str = None,        # Environnement
    prometheus_port: int = None,    # Port pour Prometheus
    log_level: int = None,          # Niveau de log
    additional_attributes: dict = None,  # Attributs supplémentaires
    otlp_endpoint: str = None,      # Endpoint OTLP
    enable_console_export: bool = None,  # Export console
    json_logs: bool = None,         # Logs JSON 
    auto_shutdown: bool = True      # Arrêt automatique
)
```

**Fonctions auxiliaires**:

- `_shutdown()`: Arrête proprement le client global
- `_function_decorator(func)`: Décore une fonction pour l'instrumenter automatiquement
- `_apply_auto_instrumentation()`: Applique l'instrumentation à tous les modules
- `_instrument_module(module)`: Instrumente un module spécifique
- `_setup_system_metrics()`: Configure les métriques système
- `_setup_data_science_instrumentation()`: Instrumente les bibliothèques de data science

### `DataLogger`

Extension du logger Python standard:

```python
class DataLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET)
    def with_data(self, **kwargs)  # Context manager pour ajouter des données
    def data(self, level, msg, data=None, *args, **kwargs)  # Logging avec données
```

### `JsonLogFormatter`

Formateur personnalisé pour les logs JSON:

```python
class JsonLogFormatter(logging.Formatter):
    def __init__(self, trace_provider=None)
    def format(self, record)  # Convertit un enregistrement en JSON
```

### Instrumentation Pandas

AutoTelemetry instrumente automatiquement les opérations Pandas courantes:

- `read_csv`: Capture le nombre de lignes, colonnes et la taille mémoire
- Opérations de traitement: `groupby`, `merge`, `join`, `concat`, `sort_values`

Pour chaque opération, des spans de trace sont créés avec des attributs comme:
- `pandas.input_rows`: Nombre de lignes en entrée
- `pandas.output_rows`: Nombre de lignes en sortie
- `pandas.filtered_rows`: Lignes supprimées
- `processing_time_ms`: Temps d'exécution

### Instrumentation NumPy

Pour les opérations NumPy comme `mean`, `median`, `std`, etc., les attributs suivants sont capturés:
- `numpy.input_size`: Taille des données d'entrée
- `processing_time_ms`: Temps d'exécution

## Flux d'Exécution Typique

1. **Initialisation**: Le client est initialisé avec `auto_instrument()`
2. **Instrumentation Automatique**: Toutes les fonctions sont automatiquement instrumentées
3. **Logs et Traces**: Chaque opération génère des logs et traces avec contexte
4. **Métriques**: Les opérations de données génèrent automatiquement des métriques
5. **Export**: Les signaux de télémétrie sont exportés vers Prometheus/OTLP
6. **Arrêt**: Le client est arrêté proprement à la fin de l'exécution

## Bonnes Pratiques

1. **Logs Structurés**: Utilisez `extra={"data": {...}}` pour des logs riches
2. **Noms de Métriques**: Suivez le pattern `domaine.entité.mesure` 
3. **Unités**: Spécifiez toujours l'unité de mesure pour les métriques
4. **Contexte**: Enrichissez les traces avec des attributs pertinents
5. **Auto-Shutdown**: Laissez le client s'arrêter proprement

## Exemple Complet

Voici un exemple complet montrant l'utilisation des principaux aspects de la bibliothèque:

```python
from autotelemetry import auto_instrument, Environment, LogLevel

# Initialisation en une ligne
client = auto_instrument(
    service_name="mon-application",
    service_version="1.0.0", 
    environment=Environment.PRODUCTION,
    json_logs=True
)

# Récupérer un logger
logger = client.get_logger()

# Créer des métriques personnalisées
counter = client.create_counter("app.requests.count", "Nombre de requêtes", "1")
latency = client.create_histogram("app.requests.latency", "Latence des requêtes", "ms")

# Logger avec contexte structuré
logger.info("Traitement démarré", extra={"data": {"job_id": "123", "user": "admin"}})

# Enregistrer des métriques
counter.add(1, {"endpoint": "/api/data"})
latency.record(42.5, {"endpoint": "/api/data"})

# Utilisation du tracer directement pour des spans personnalisés
with client.tracer.start_as_current_span("opération-personnalisée") as span:
    span.set_attribute("attribut.custom", "valeur")
    # Opération...

# Arrêt propre (facultatif si auto_shutdown=True)
client.shutdown()
```

La documentation ci-dessus devrait vous aider à présenter en détail la bibliothèque AutoTelemetry, en montrant comment elle standardise et simplifie l'observabilité dans les applications Python. 