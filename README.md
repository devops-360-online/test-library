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

- **Auto-instrumente** automatiquement votre code avec une seule ligne
- **Standardise** les noms, formats et attributs à l'échelle de l'organisation
- **Réduit le code d'initialisation** à une seule ligne
- **Adapte automatiquement** son comportement selon l'environnement (dev, test, prod)
- **Spécialise les abstractions** pour les opérations de traitement de données

## Auto-instrumentation

Notre bibliothèque permet une auto-instrumentation avec un minimum d'effort :

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

La bibliothèque va automatiquement :
- Tracer toutes les fonctions
- Collecter les métriques système et applicatives
- Logger les informations pertinentes
- Mesurer les performances
- Détecter les anomalies

## Avantages pour les équipes

1. **Simplicité maximale** : Une seule ligne pour activer toute l'observabilité
2. **Standardisation** : Toutes les applications suivent les mêmes pratiques d'observabilité
3. **Productivité** : Réduction du temps de développement consacré à l'observabilité
4. **Facilité de maintenance** : Centralisation des standards et mises à jour
5. **Visibilité améliorée** : Dashboards et alertes cohérents grâce aux standards

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