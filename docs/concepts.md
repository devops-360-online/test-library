# Concepts Fondamentaux

Ce document explique les concepts essentiels d'observabilité implémentés dans notre bibliothèque `simple_observability`.

## Les Trois Piliers de l'Observabilité

L'observabilité moderne repose sur trois piliers complémentaires :

### 1. Métriques

Les **métriques** sont des valeurs numériques collectées à intervalles réguliers, représentant l'état du système à un moment donné.

**Types de métriques implémentés :**
- **Compteurs** : Des valeurs monotones croissantes (ex: nombre de lignes traitées)
- **Jauges** : Des valeurs qui peuvent augmenter ou diminuer (ex: utilisation mémoire)
- **Histogrammes** : Distribution des valeurs mesurées (ex: temps de traitement)

**Standards imposés par notre bibliothèque :**
- Noms de métriques en snake_case (`data_rows_processed_total`)
- Suffixes standardisés (`_total`, `_seconds`, `_bytes`)
- Unités cohérentes (`s` pour secondes, `By` pour bytes, etc.)
- Attributs standards inclus (service, environnement, etc.)

### 2. Logs

Les **logs** sont des enregistrements textuels d'événements qui se produisent dans le système.

**Caractéristiques implémentées :**
- **Logs structurés** : Format JSON en production
- **Contexte de trace** : Inclusion automatique des identifiants de trace
- **Niveaux standardisés** : DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Attributs de contexte** : Possibilité d'ajouter des informations structurées

**Standards imposés :**
- Format cohérent avec informations de base toujours incluses
- Propagation automatique du contexte de traçage
- Ajout facile de métadonnées structurées

### 3. Traces

Les **traces** capturent le flux d'exécution d'une requête ou opération à travers le système.

**Concepts clés implémentés :**
- **Spans** : Opérations individuelles au sein d'une trace
- **Contexte de trace** : Identifiants partagés entre composants
- **Attributs** : Métadonnées attachées aux spans
- **Évènements** : Points d'intérêt dans une span

**Standards imposés :**
- Nommage cohérent des spans (`data.load`, `data.transform`)
- Attributs standards pour les opérations de données
- Détection automatique de la taille des DataFrames
- Propagation du contexte entre logs et traces

## Standards d'Intégration

Notre bibliothèque implémente des standards d'intégration pour assurer la cohérence :

### OpenTelemetry

[OpenTelemetry](https://opentelemetry.io/) est la base technologique de notre solution, offrant:
- Un format standard pour les métriques, logs et traces
- Des exporters vers différentes destinations
- Une propagation de contexte entre services

### Prometheus

[Prometheus](https://prometheus.io/) est utilisé pour le stockage et l'interrogation des métriques:
- Exposition des métriques sur un endpoint HTTP
- Format de métriques compatible
- Capacités de scraping pour la collecte

### Standards de Nommage

Notre bibliothèque définit des standards de nommage clairs:

```
<domaine>_<entité>_<action>_<unité>[_total]
```

Exemples:
- `http_requests_duration_seconds`
- `data_rows_processed_total`
- `memory_usage_bytes`

### Standards d'Attributs

Les attributs (ou labels) sont standardisés:
- `service.name`: Nom du service
- `service.version`: Version du service
- `deployment.environment`: Environnement (prod, dev, etc.)
- `data.source`: Source de données
- `data.operation`: Type d'opération sur les données

## Architecture d'Observabilité

Notre bibliothèque s'intègre dans une architecture d'observabilité moderne:

```
Application (avec simple_observability)
    ↓
OpenTelemetry Collector (optionnel)
    ↓
┌─────────────┬─────────────┬─────────────┐
│ Prometheus  │ Elastic/    │ Jaeger/     │
│ (Métriques) │ Loki (Logs) │ Tempo       │
└─────────────┴─────────────┴─────────────┘
                    ↓
                 Grafana
               (Visualisation)
```

## Concepts Avancés

### Auto-instrumentation

Notre bibliothèque offre une **auto-instrumentation** qui:
- Injecte automatiquement des métriques, logs et traces pertinents
- Détecte la forme des données traitées
- Standardise les noms et attributs
- Adapte le comportement à l'environnement

### Corrélation des Signaux

La corrélation entre métriques, logs et traces est automatique:
- IDs de trace inclus dans les logs
- Métriques liées aux opérations tracées
- Timestamps alignés entre les différents signaux

### Instrumentation Contextuelle

Les contextes permettent d'enrichir automatiquement tous les signaux:
- `timed_task` pour instrumenter une tâche complète
- `data_operation` pour les opérations spécifiques aux données
- `with_data` pour enrichir les logs avec des métadonnées

## Ressources externes

- [Documentation OpenTelemetry](https://opentelemetry.io/docs/)
- [Documentation Prometheus](https://prometheus.io/docs/introduction/overview/)
- [Documentation Grafana](https://grafana.com/docs/) 