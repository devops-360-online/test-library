# Simple Observability

Une bibliothèque Python simplifiant l'utilisation d'OpenTelemetry pour standardiser les métriques, logs et traces dans les applications de traitement de données.

## Pourquoi cette bibliothèque ?

### Le problème

L'observabilité moderne repose sur trois piliers fondamentaux : les métriques, les logs et les traces distribuées. Cependant, l'implémentation de ces trois composants présente plusieurs défis :

1. **Complexité technique** : OpenTelemetry est puissant mais complexe, avec des APIs distinctes pour chaque pilier.
2. **Code répétitif** : Les développeurs écrivent le même code d'initialisation dans chaque application.
3. **Inconsistance** : Sans standards, chaque équipe implémente différemment les noms de métriques, formats de logs, etc.
4. **Courbe d'apprentissage** : Les développeurs doivent comprendre OpenTelemetry avant de pouvoir instrumenter leurs applications.
5. **Fragmentation** : De nombreuses bibliothèques tierces à intégrer et maintenir.

### Notre solution

`simple_observability` est une bibliothèque d'auto-instrumentation qui :

- **Unifie les trois piliers** sous une API simple et cohérente
- **Standardise** les noms, formats et attributs à l'échelle de l'organisation
- **Réduit le code d'initialisation** de plus de 100 lignes à moins de 10
- **Adapte automatiquement** son comportement selon l'environnement (dev, test, prod)
- **Spécialise les abstractions** pour les opérations de traitement de données

## Auto-instrumentation

Notre bibliothèque permet une auto-instrumentation avec un minimum d'effort :

```python
# Une seule ligne pour initialiser toute l'observabilité
from simple_observability import ObservabilityClient
obs = ObservabilityClient(service_name="mon-service")

# Obtenir un logger pré-configuré
logger = obs.get_logger()

# Instrumenter automatiquement une fonction de traitement de données
@obs.trace_data_processing()
def process_dataframe(df):
    logger.info(f"Traitement de {len(df)} lignes")
    # ... logique de traitement ...
    return result

# Créer des métriques standard en une ligne
metrics = obs.create_data_processing_metrics()
```

## Avantages pour les équipes

1. **Standardisation** : Toutes les applications suivent les mêmes pratiques d'observabilité
2. **Productivité** : Réduction du temps de développement consacré à l'observabilité
3. **Facilité de maintenance** : Centralisation des standards et mises à jour
4. **Visibilité améliorée** : Dashboards et alertes cohérents grâce aux standards
5. **Formation simplifiée** : Les développeurs peuvent instrumenter sans être experts en observabilité

## Prérequis

### Dépendances Python

```
Python >= 3.8
opentelemetry-api >= 1.18.0
opentelemetry-sdk >= 1.18.0
opentelemetry-exporter-otlp >= 1.18.0
opentelemetry-exporter-prometheus >= 1.18.0
prometheus-client >= 0.16.0
```

### Infrastructure (optionnelle)

Pour exploiter pleinement cette bibliothèque en production :

- **Prometheus** : Pour stocker et interroger les métriques
- **Grafana** : Pour visualiser les métriques
- **OpenTelemetry Collector** : Pour recevoir et router les données de télémétrie
- **Jaeger ou Zipkin** : Pour visualiser les traces distribuées

## Installation

```bash
pip install simple_observability
```

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