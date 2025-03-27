
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

## Exportation des données

**Mini-Telemetry exporte exclusivement vers stdout (la sortie standard)**:

- **Aucun composant externe requis** pour visualiser les données
- **Tout apparaît directement dans la console/terminal**
- **Parfait pour le développement et le debug**
- Un autre composant séparé peut collecter cette sortie si nécessaire (Filebeat, Fluentd, etc.)

Format des sorties:
1. **Logs**: Texte formaté ou JSON, avec IDs de trace
2. **Traces**: JSON formaté avec structure de span complète
3. **Métriques**: JSON formaté avec valeurs et timestamps

Cette approche minimaliste permet de:
- Commencer immédiatement sans infrastructure complexe
- Voir toutes les données au même endroit
- Utiliser les outils standard de redirection UNIX si nécessaire (`> file.log`)
- Intégrer facilement à des conteneurs Docker ou des environnements cloud

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

## Extension à d'autres backends (optionnel)

Par défaut, les traces, logs et métriques sont envoyés **uniquement à la console (stdout)**, sans nécessiter de composants externes.

Si vous souhaitez ultérieurement exporter vers d'autres systèmes, voici comment procéder:

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

Cette extension est entièrement optionnelle et n'est recommandée que lorsque votre projet atteint une maturité nécessitant une infrastructure d'observabilité complète.

## Ressources

- [Documentation OpenTelemetry](https://opentelemetry.io/docs/)
- [Spécification OpenTelemetry](https://github.com/open-telemetry/opentelemetry-specification)
- [Conventions sémantiques](https://github.com/open-telemetry/opentelemetry-specification/tree/main/specification/trace/semantic_conventions) 