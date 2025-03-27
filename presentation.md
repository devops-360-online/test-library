# Présentation: Mini-Telemetry et OpenTelemetry

## Qu'est-ce que l'observabilité?

L'observabilité répond à la question: **"Pourquoi mon système se comporte-t-il ainsi?"**

Elle se compose de trois piliers :
- **Traces**: Suivi du chemin d'exécution à travers le système
- **Métriques**: Mesures numériques de performance et d'état
- **Logs**: Enregistrements d'événements et de messages

## Le problème à résoudre

Aujourd'hui, nous rencontrons plusieurs défis :

- **Systèmes complexes**: Multiples services, microservices, dépendances externes
- **Sources de données fragmentées**: Chaque outil a son propre format et stockage
- **Manque de corrélation**: Difficile de relier un log à une trace ou une métrique
- **Temps de résolution**: Identifier et résoudre les problèmes prend trop de temps

## Qu'est-ce qu'OpenTelemetry?

OpenTelemetry est un standard ouvert et une boîte à outils pour l'observabilité.

**Points clés** :
- Projet de la Cloud Native Computing Foundation (CNCF)
- Fusion d'OpenCensus (Google) et OpenTracing (CNCF)
- Support pour tous les langages majeurs
- Indépendant des fournisseurs de solutions d'observabilité

## Architecture OpenTelemetry

![Architecture OpenTelemetry](https://opentelemetry.io/img/otel-diagram.svg)

1. **API**: Interfaces pour instrumenter le code
2. **SDK**: Implémentation des API
3. **Collecteur**: Réception, traitement et export des données
4. **Backends**: Stockage et visualisation (Jaeger, Prometheus, Elasticsearch, etc.)

## Pourquoi utiliser OpenTelemetry?

1. **Standard ouvert**: Ne vous enferme pas avec un fournisseur
2. **Vue unifiée**: Corrélation native entre traces, métriques et logs
3. **Extensible**: Supporte de multiples backends
4. **Riche en fonctionnalités**: Auto-instrumentation, échantillonnage, etc.
5. **Large adoption**: Utilisé par Google, Microsoft, AWS, etc.

## Notre Solution: Mini-Telemetry

Nous avons créé une bibliothèque minimaliste qui :

1. **Simplifie la configuration** d'OpenTelemetry
2. **Expose les interfaces standards** pour l'instrumentation
3. **Configure la corrélation** entre traces, logs et métriques
4. **Laisse le contrôle aux développeurs** sur l'instrumentation
5. **Exporte exclusivement vers stdout** (aucun composant externe requis)

## Exportation "Zero-Infra"

Un principe fondamental de Mini-Telemetry:

- **Export exclusif vers stdout** (la sortie standard)
- **Aucun composant externe requis** pour voir les données
- **Tout apparaît directement dans le terminal/console**
- **"Ce que vous voyez est ce que vous obtenez"**

![Flux d'exportation simplifié](https://mermaid.ink/img/pako:eNp1kV9PgzAUxb9K03cweAGCDI2uxMQ4g4kDX3ygXGnNgNK0HWEsxO-uMBzO5QX6O7-ec9uDyAtBIQW5k_L1jdfYlArFZ1OhcdFV-cEbDMZLJZtDJpSBDzEOYnEu1PKNPazwXm6RGVGDVlUrtMGL_DfPqCPkG0h_eSRSNTnS66VJFz3J1ZP-OXAOH16hd6V1HVYWCx_tULO21Rp-rHWCaxSyFBw6-tL1pqUcqqvQ_6EFXFPvV_iXRTB4JKPYGw-HYRQOxyEh0eiRPM9kHo-cW6M4kCIrrEKnrTm_3cR-Bveh4mAbOMXKJkfWlvQG0tJ2f6x-6p-Q4-4j0pLbkKa0MqZJSBC4E8-NXJLQnQbXhDRdNvpGCylz2PahJJt6P5TQ7LsHxYA2QpVQaCOaI6SKF9C5U8AxBDTVGXSZbqQqoOtDrQ-dqr3HyxHSEgCtuIPWOA_e7m7pOG73DVAW6y4?type=png)

Cette approche permet de:
- **Démarrer immédiatement** sans infrastructure complexe
- **Voir toutes les données** dans le même flux
- **Intégrer facilement** avec les outils standard Unix
- **Collecter optionnellement** avec un outil externe quand nécessaire

## Fonctionnement de Mini-Telemetry

1. **Une seule initialisation** pour configurer tous les outils :
```python
telemetry = TelemetryTools(
    service_name="mon-service",
    service_version="1.0.0"
)
```

2. **Outils exposés** pour chaque composant :
```python
tracer = telemetry.get_tracer("mon.composant")
meter = telemetry.get_meter("mon.composant")
logger = telemetry.get_logger("mon.composant")
```

3. **Instrumentation manuelle** précise et contrôlée :
```python
with tracer.start_as_current_span("opération") as span:
    span.set_attribute("clé", "valeur")
    logger.info("Opération en cours")  # Automatiquement lié à la trace
    meter.create_counter("compteur").add(1)
```

## Traces: Comment ça marche

Une **trace** est un arbre de **spans** :

```
Trace
├── Span A (requête HTTP)
│   ├── Span B (validation)
│   ├── Span C (accès DB)
│   │   └── Span D (requête SQL)
│   └── Span E (formatage réponse)
```

Chaque span contient :
- Nom
- Début/Fin de l'opération
- Attributs (clé-valeur)
- Événements
- Statut (succès/échec)

## Démonstration de traçage

```python
def traiter_commande(commande_id):
    # Créer un span parent
    with tracer.start_as_current_span("traiter_commande") as span:
        span.set_attribute("commande.id", commande_id)
        
        # Logger avec contexte de trace automatique
        logger.info(f"Traitement commande {commande_id} démarré")
        
        # Sous-opérations (spans enfants)
        with tracer.start_as_current_span("valider_commande"):
            # Validation...
            pass
            
        with tracer.start_as_current_span("paiement"):
            # Paiement...
            if problème:
                # Gestion d'erreur
                span.set_status(trace.Status(trace.StatusCode.ERROR))
                logger.error("Échec du paiement")
```

## Métriques: Types et Utilisation

Types de métriques :
- **Compteurs**: Valeurs qui ne peuvent qu'augmenter
- **Histogrammes**: Distributions de valeurs
- **Jauges**: Valeurs qui peuvent augmenter/diminuer

```python
# Compteur - par ex. nombre de requêtes
requests = meter.create_counter("requêtes.total")
requests.add(1, {"endpoint": "/api/users"})

# Histogramme - par ex. temps de réponse
latency = meter.create_histogram("requêtes.latence")
latency.record(42.5, {"endpoint": "/api/users"})

# Jauge - par ex. connexions actives
# (non directement supporté, utiliser UpDownCounter)
```

## Logs avec Contexte de Trace

Les logs sont automatiquement enrichis avec les ID de trace et de span :

```python
# Dans un span
with tracer.start_as_current_span("opération") as span:
    # Ce log contiendra automatiquement les ID de trace et span
    logger.info("Message dans l'opération")
```

Format de log résultant :
```
2023-03-27 14:23:45 [INFO] service - trace_id=abcdef... span_id=123456... - Message dans l'opération
```

## Corrélation: La Puissance d'OpenTelemetry

La corrélation permet de naviguer entre les différents signaux :

1. **Problème détecté dans les métriques** (ex: pic de latence)
2. **Exploration des traces correspondantes** (via attributs communs)
3. **Analyse des logs spécifiques** (via trace_id et span_id)

Notre bibliothèque configure automatiquement cette corrélation.

## Cas d'Usage Concrets

1. **Détection et analyse d'anomalies** :
   - Les métriques montrent un pic de latence
   - Les traces identifient les requêtes lentes
   - Les logs révèlent la cause racine

2. **Suivi des transactions business** :
   - Voir le parcours complet d'une commande
   - Identifier les étapes problématiques
   - Mesurer les délais par étape

3. **Optimisation de performance** :
   - Identifier les goulots d'étranglement
   - Mesurer l'impact des optimisations
   - Suivre les métriques dans le temps

## Visualisation (Backends)

Avec notre approche "zero-infra":

- **Terminal/Console**: Visualisation directe et immédiate
- **Redirection UNIX**: `python votre_script.py > logs.txt`
- **Collecte optionnelle**: Un autre composant séparé peut collecter stdout

Si vous souhaitez éventuellement étendre vers des outils spécialisés:
- **Traces**: Jaeger, Zipkin, Tempo
- **Métriques**: Prometheus, Grafana
- **Logs**: Elasticsearch, Loki

> L'extension est entièrement optionnelle et peut être ajoutée progressivement lorsque vos besoins grandissent.

## Prochaines Étapes

1. **Adoption immédiate** :
   - Utiliser Mini-Telemetry sans aucune infrastructure supplémentaire
   - Instrumenter progressivement les parties critiques

2. **Standardisation** :
   - Adopter des conventions de nommage cohérentes
   - Utiliser les mêmes attributs dans toute l'organisation

3. **Évolution progressive** (si nécessaire) :
   - Commencer avec l'export vers stdout uniquement
   - Ajouter des exportateurs pour des systèmes spécialisés au besoin

## Conclusion

Mini-Telemetry facilite l'adoption d'OpenTelemetry en :

1. **Simplifiant la configuration**
2. **Exposant des interfaces simples et standardisées**
3. **Automatisant la corrélation** entre traces, métriques et logs
4. **Laissant le contrôle aux développeurs** sur l'instrumentation
5. **Fonctionnant sans infrastructure externe** (export vers stdout)

**Résultat** : Une observabilité complète avec un minimum d'effort d'intégration et aucun besoin d'infrastructure supplémentaire.

## Questions ?

N'hésitez pas à poser vos questions ! 