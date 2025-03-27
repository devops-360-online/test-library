#!/usr/bin/env python3
"""
Exemple simple d'utilisation d'AutoTelemetry
-------------------------------------------

Cet exemple illustre:
- L'initialisation d'AutoTelemetry
- Les logs JSON structurés
- La création de métriques personnalisées
- La gestion d'erreurs avec traces
"""

import pandas as pd
import numpy as np
import time
import random
import sys
from datetime import datetime

# Ajouter le répertoire parent au chemin d'importation
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from autotelemetry import LogLevel, Environment, SimpleObservabilityClient

# Initialiser AutoTelemetry (sans l'auto-instrumentation)
client = SimpleObservabilityClient(
    service_name="exemple-simple",
    service_version="1.0.0",
    environment=Environment.DEVELOPMENT,  # En production, les logs JSON sont obligatoires
    log_level=LogLevel.INFO,
    prometheus_port=8765  # Utiliser un port différent pour éviter les conflits
)

# Obtenir un logger configuré
logger = client.get_logger()

# Créer quelques métriques personnalisées
metrics = {
    "rows_processed": client.create_counter(
        name="exemple.rows_processed", 
        description="Nombre de lignes traitées",
        unit="1"
    ),
    "processing_time": client.create_histogram(
        name="exemple.processing_time", 
        description="Temps de traitement",
        unit="ms"
    ),
    "data_quality": client.create_histogram(
        name="exemple.data_quality",
        description="Qualité des données (ratio de valeurs valides)",
        unit="1"
    )
}

def generate_data(rows=1000):
    """Génère des données synthétiques pour l'exemple."""
    logger.info(f"Génération de {rows} lignes de données")
    
    # Créer un DataFrame avec des données aléatoires
    df = pd.DataFrame({
        "id": range(1, rows + 1),
        "timestamp": [datetime.now().isoformat() for _ in range(rows)],
        "valeur": np.random.normal(50, 20, rows),
        "categorie": np.random.choice(["A", "B", "C", "D"], rows),
        "est_valide": np.random.choice([True, False], rows, p=[0.9, 0.1])
    })
    
    # Logger des informations sur les données générées
    logger.info("Données générées avec succès", extra={"data": {
        "rows": len(df),
        "categories": df["categorie"].value_counts().to_dict(),
        "valeur_moyenne": df["valeur"].mean(),
        "ratio_valides": df["est_valide"].mean()
    }})
    
    return df

def process_data(df):
    """Traite le DataFrame et enregistre des métriques."""
    start_time = time.time()
    
    # Simuler un temps de traitement variable
    time.sleep(random.uniform(0.1, 0.3))
    
    # Filtrer les données valides
    df_filtered = df[df["est_valide"]]
    
    # Calculer quelques statistiques
    stats_by_category = df_filtered.groupby("categorie")["valeur"].agg(["count", "mean", "std"])
    
    # Enregistrer des métriques
    metrics["rows_processed"].add(len(df))
    metrics["processing_time"].record((time.time() - start_time) * 1000)
    metrics["data_quality"].record(df["est_valide"].mean())
    
    # Logger les résultats avec des données structurées
    logger.info("Traitement terminé", extra={"data": {
        "operation": "aggregation",
        "timestamp": datetime.now().isoformat(),
        "rows_total": len(df),
        "rows_valid": len(df_filtered),
        "processing_time_ms": (time.time() - start_time) * 1000,
        "stats": stats_by_category.to_dict()
    }})
    
    return df_filtered, stats_by_category

def simulate_error(chance=0.3):
    """Simule une erreur aléatoire pour démontrer la gestion d'erreurs."""
    if random.random() < chance:
        logger.warning("Opération susceptible d'échouer", extra={"data": {"chance": chance}})
        raise ValueError("Erreur simulée pour la démonstration")

def main():
    """Fonction principale de l'exemple."""
    logger.info("Démarrage de l'exemple AutoTelemetry")
    
    try:
        # Générer des données
        df = generate_data(rows=random.randint(500, 1500))
        
        # Simuler une erreur potentielle
        simulate_error(chance=0.3)
        
        # Traiter les données
        df_filtered, stats = process_data(df)
        
        # Afficher quelques résultats
        logger.info("Résumé des statistiques", extra={"data": {
            "total_rows": len(df),
            "valid_rows": len(df_filtered),
            "categories": len(stats)
        }})
        
    except Exception as e:
        # Les exceptions sont automatiquement liées aux traces
        logger.error(f"Erreur dans l'exécution: {str(e)}")
    finally:
        # Fermeture propre (bien que ce soit fait automatiquement à la fin du programme)
        logger.info("Arrêt de l'exemple")
        client.shutdown()

if __name__ == "__main__":
    main() 