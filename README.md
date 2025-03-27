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

# Mini-Telemetry: Une bibliothèque minimaliste pour OpenTelemetry

Cette bibliothèque simplifie l'utilisation d'OpenTelemetry en fournissant une interface minimaliste pour configurer et exposer les outils d'observabilité (traces, logs et métriques).

## Qu'est-ce qu'OpenTelemetry?

OpenTelemetry est un framework standard, open-source, pour collecter et envoyer des données d'observabilité (traces, métriques et logs) à partir de vos applications.

### Les trois piliers de l'observabilité

1. **Traces**: Suivent le flux d'exécution à travers les composants de votre application
2. **Métriques**: Capturent des valeurs numériques sur l'état et la performance
3. **Logs**: Enregistrent des événements et des messages textuels

### Avantages d'OpenTelemetry

- **Standard ouvert**: Compatible avec de nombreux fournisseurs
- **Pas de verrouillage**: Vous pouvez changer de backend d'analyse à tout moment
- **Intégré**: Corrèle naturellement les traces, métriques et logs
- **Extensible**: Fonctionne avec tous les langages et frameworks

## Installation

```bash
pip install opentelemetry-api opentelemetry-sdk
```

## Utilisation de base

```python
from mini_telemetry import TelemetryTools

# 1. Initialisation (fait une seule fois)
telemetry = TelemetryTools(
    service_name="mon-service",
    service_version="1.0.0",
    environment="production"
)

# 2. Obtenir les outils pour chaque composant
tracer = telemetry.get_tracer("mon.module")
meter = telemetry.get_meter("mon.module")
logger = telemetry.get_logger("mon.module")

# 3. Utiliser ces outils dans votre code
```

## Guide des concepts OpenTelemetry

### Traces et Spans

Une **trace** représente le chemin d'exécution complet à travers le système. Elle est composée de **spans** interconnectés.

Un **span** représente une opération unique dans votre code avec:
- Un nom
- Un temps de début/fin
- Des attributs (clé-valeur)
- Des événements horodatés
- Des liens vers d'autres spans
- Un statut (succès/échec)

```python
# Créer un span parent
with tracer.start_as_current_span("opération-principale") as span:
    # Ajouter des attributs
    span.set_attribute("utilisateur.id", "123")
    
    # Effectuer l'opération...
    
    # Créer un span enfant (sous-opération)
    with tracer.start_as_current_span("sous-opération") as child:
        # Opération enfant...
        pass
    
    # Enregistrer un événement
    span.add_event("événement-important", {"détail": "valeur"})
    
    # Définir le statut
    span.set_status(trace.Status(trace.StatusCode.OK))
```

### Métriques

Les métriques sont des mesures numériques collectées sur une période. Types principaux:

1. **Compteur**: Valeur qui ne peut qu'augmenter (ex: nombre de requêtes)
2. **Histogramme**: Distribution de valeurs (ex: temps de réponse)
3. **Jauge**: Valeur qui peut augmenter/diminuer (ex: utilisation mémoire)

```python
# Créer un compteur
counter = meter.create_counter(
    name="requêtes",
    description="Nombre de requêtes traitées",
    unit="1"  # Pas d'unité spécifique
)

# Incrémenter le compteur (avec attributs)
counter.add(1, {"endpoint": "/api", "méthode": "GET"})

# Créer un histogramme
histogram = meter.create_histogram(
    name="latence",
    description="Temps de réponse des requêtes",
    unit="ms"  # Millisecondes
)

# Enregistrer une valeur
histogram.record(42.5, {"endpoint": "/api"})
```

### Logs avec contexte de trace

Les logs peuvent être enrichis avec les identifiants de trace et de span, permettant de les corréler avec les traces:

```python
# Le logger est configuré pour ajouter automatiquement les IDs de trace et span
logger.info("Traitement démarré")
logger.error("Une erreur s'est produite", exc_info=True)

# Avec contexte supplémentaire
logger.info("Opération terminée", extra={"durée_ms": 123, "status": "success"})
```

## Corrélation entre traces, métriques et logs

La corrélation est l'un des aspects les plus puissants d'OpenTelemetry:

1. **Logs → Traces**: Les logs incluent automatiquement des IDs de trace/span
2. **Traces → Métriques**: Les attributs de span peuvent être appliqués aux métriques
3. **Métriques → Traces**: Les problèmes détectés dans les métriques peuvent être explorés via les traces associées

Exemple de log avec contexte de trace:
```
2023-03-27 14:23:45 [INFO] mon.module - trace_id=abcdef0123456789 span_id=0123456789abcdef - Message
```

## Bonnes pratiques

1. **Conventions de nommage**:
   - Services: `com.entreprise.service`
   - Spans: `opération.action` (ex: `http.request`, `db.query`)
   - Métriques: `domaine.objet.mesure` (ex: `http.server.duration_ms`)

2. **Attributs cohérents**: Utilisez les mêmes attributs pour les spans et métriques associées
```python
# Dans un span
span.set_attribute("endpoint", "/api/users")

# Dans une métrique (même attribut)
counter.add(1, {"endpoint": "/api/users"})
```

3. **Granularité des spans**: 
   - Créez des spans pour les opérations significatives
   - Utilisez des spans imbriqués pour les sous-opérations
   - Ne tracez pas les fonctions triviales

4. **Gestion des erreurs**:
```python
try:
    # Code
except Exception as e:
    # Enregistrer l'exception dans le span
    span.record_exception(e)
    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
    logger.error(f"Erreur: {str(e)}", exc_info=True)
    raise
```

## Exemple complet

Voir le fichier [mini_telemetry.py](mini_telemetry.py) pour un exemple complet de:
- Configuration des outils
- Instrumentation manuelle
- Corrélation entre traces, métriques et logs

## Extension à d'autres backends

Par défaut, les traces, logs et métriques sont envoyés à la console, mais il est facile d'étendre vers:

- **Jaeger/Zipkin** pour les traces
- **Prometheus** pour les métriques
- **Elasticsearch** pour les logs

Exemple d'ajout d'exportateur OTLP:

```python
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Dans _setup_tracing()
otlp_exporter = OTLPSpanExporter(endpoint="http://collector:4317")
span_processor = BatchSpanProcessor(otlp_exporter)
trace_provider.add_span_processor(span_processor)
```

## Ressources

- [Documentation OpenTelemetry](https://opentelemetry.io/docs/)
- [Spécification OpenTelemetry](https://github.com/open-telemetry/opentelemetry-specification)
- [Conventions sémantiques](https://github.com/open-telemetry/opentelemetry-specification/tree/main/specification/trace/semantic_conventions) 