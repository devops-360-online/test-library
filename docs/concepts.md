# Concepts fondamentaux

Cette documentation présente les concepts clés de l'observabilité et comment ils sont implémentés dans la bibliothèque `autotelemetry`.

## Auto-instrumentation

L'auto-instrumentation est la fonctionnalité centrale de `autotelemetry`. Elle permet d'instrumenter automatiquement votre code sans avoir à modifier votre code métier existant.

### Comment fonctionne l'auto-instrumentation

Lorsque vous appelez `auto_instrument()`, la bibliothèque:

1. **Modifie le mécanisme d'import de Python** pour intercepter les imports de modules
2. **Instrumente automatiquement les fonctions** en les décorant avec un tracer
3. **Configure les exportateurs** pour les métriques, logs (JSON) et traces
4. **Intègre les bibliothèques de data science** comme Pandas pour capturer des métriques spécifiques
5. **Collecte automatiquement les métriques système** comme l'utilisation CPU et mémoire

Cette approche permet d'ajouter une observabilité complète à votre application avec une seule ligne de code, sans compromettre la lisibilité ou la maintenabilité de votre code métier.

## Les trois piliers de l'observabilité 

### Métriques

Les métriques sont des valeurs numériques collectées à intervalles réguliers pour mesurer les performances et l'état de votre application.

#### Types de métriques

- **Compteurs**: Valeurs qui ne peuvent qu'augmenter (ex: nombre de requêtes)
- **Histogrammes**: Distribution de valeurs (ex: temps de réponse)
- **Jauges**: Valeurs qui peuvent augmenter ou diminuer (ex: utilisation mémoire)

#### Métriques collectées automatiquement

- **Métriques système**: CPU, mémoire, garbage collector
- **Métriques d'exécution**: Durée des appels de fonctions, nombre d'appels
- **Métriques de données**: Pour les DataFrames pandas: nombre de lignes, taille mémoire

#### Standards de nommage

- `service.{métrique}`: Métriques liées au service
- `system.{ressource}.{métrique}`: Métriques système
- `function.{métrique}`: Métriques de fonction
- `data.{métrique}`: Métriques liées aux données

### Logs

Les logs sont des enregistrements textuels d'événements qui se produisent dans votre application.

#### La normalisation JSON obligatoire

Notre bibliothèque **impose le format JSON** pour tous les logs, garantissant une structure cohérente et exploitable à l'échelle de toute l'organisation.

Avantages de cette normalisation:
- **Facilité d'analyse**: Les logs structurés permettent des requêtes complexes
- **Efficacité opérationnelle**: Moins de temps perdu à parser des formats incohérents
- **Intégration simplifiée**: Compatible avec les outils modernes d'analyse de logs
- **Contexte enrichi**: Chaque log contient automatiquement des métadonnées standardisées

#### Caractéristiques des logs

- **JSON obligatoire**: Format structuré avec champs standardisés
- **Contexte de trace**: Inclusion des IDs de trace et span
- **Niveaux standardisés**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Attributs obligatoires**: service.name, timestamp, level, etc.

#### Standards de formatage

- Timestamp au format ISO 8601
- Inclut service, composant, niveau, message
- Métadonnées structurées pour faciliter la recherche
- Schéma JSON validé

#### Exemple de log JSON standardisé

```json
{
  "timestamp": "2023-06-15T14:32:45.123Z",
  "level": "ERROR",
  "logger": "data_pipeline",
  "message": "Échec du traitement",
  "service.name": "mon-service",
  "service.version": "1.0.0",
  "deployment.environment": "production",
  "trace_id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "span_id": "b2c3d4e5f6g7h8i9",
  "exception": {
    "type": "ValueError",
    "message": "Données invalides",
    "traceback": "..."
  },
  "data": {
    "job_id": "12345",
    "input_rows": 1000,
    "stage": "transform"
  }
}
```

### Traces

Les traces capturent le flux d'exécution des requêtes à travers votre application, permettant de comprendre le chemin d'exécution et d'identifier les goulots d'étranglement.

#### Éléments des traces

- **Spans**: Unités de travail individuelles
- **Contexte de trace**: Propagé à travers les appels de fonction
- **Attributs**: Métadonnées attachées aux spans
- **Événements**: Points d'intérêt dans une span

#### Standards de nommage des spans

- `{module}.{fonction}`: Nom automatique pour les fonctions
- `pandas.{opération}`: Pour les opérations Pandas
- `data.{opération}`: Pour les opérations de données génériques

## Intégration avec les standards

### OpenTelemetry

La bibliothèque utilise OpenTelemetry comme fondation technologique, fournissant:

- Un format standard pour les signaux d'observabilité
- Une API cohérente entre différents langages
- Une extensibilité via des exportateurs pluggables

### Prometheus

Pour les métriques, la bibliothèque s'intègre avec Prometheus:

- Exposition des métriques sur un endpoint HTTP
- Support pour le scraping par Prometheus
- Compatibilité avec Grafana pour la visualisation

### Elasticsearch

Pour les logs JSON standardisés, la bibliothèque s'intègre parfaitement avec Elasticsearch:

- Format JSON natif compatible avec Elasticsearch
- Indexation efficace sans transformation nécessaire
- Facilite les requêtes structurées et l'analyse

## Architecture d'observabilité

Voici comment `autotelemetry` s'intègre dans une architecture d'observabilité moderne:

```
  Votre Application                   Infrastructure d'Observabilité
┌─────────────────────┐             ┌───────────────────────────────┐
│                     │             │                               │
│  Code métier        │             │                               │
│  + auto_instrument()│───Traces────▶  OpenTelemetry Collector      │
│                     │             │                               │
│                     │───Logs JSON─▶│                ┌─────────────┐│
│                     │             │                │             ││
│                     │             │                │  Jaeger     ││
│                     │             │                │  (Traces)   ││
│                     │             │                │             ││
│                     │───Métriques─▶─────┐          └─────────────┘│
│                     │             │     │                         │
└─────────────────────┘             │     ▼          ┌─────────────┐│
                                    │  ┌─────────┐   │             ││
                                    │  │         │   │Elasticsearch││
                                    │  │Prometheus│   │  (Logs)     ││
                                    │  │         │   │             ││
                                    │  └─────────┘   └─────────────┘│
                                    │       │                       │
                                    │       │        ┌─────────────┐│
                                    │       │        │             ││
                                    │       └────────▶  Grafana    ││
                                    │                │ (Dashboards)││
                                    │                │             ││
                                    │                └─────────────┘│
                                    └───────────────────────────────┘
```

## Concepts avancés

### Auto-instrumentation profonde

La bibliothèque ne se contente pas d'instrumenter les fonctions de votre code, elle analyse également leur signature, arguments et valeurs de retour pour enrichir automatiquement les traces avec des métadonnées pertinentes.

### Corrélation de signaux

Les trois piliers (métriques, logs, traces) sont automatiquement corrélés:

- Les logs JSON incluent toujours les IDs de trace et span
- Les métriques et traces partagent des attributs communs
- Un événement peut être suivi à travers les trois piliers

### Instrumentation contextuelle

L'instrumentation adapte automatiquement son comportement selon:

- Le type de fonction (traitement de données, IO, etc.)
- L'environnement d'exécution (dev, test, prod)
- Les bibliothèques utilisées (pandas, numpy, etc.)

### Ressources externes

- [Documentation OpenTelemetry](https://opentelemetry.io/docs/)
- [Documentation Prometheus](https://prometheus.io/docs/introduction/overview/)
- [Documentation Grafana](https://grafana.com/docs/)
- [Documentation Elasticsearch](https://www.elastic.co/guide/index.html) 