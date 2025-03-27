#!/usr/bin/env python3
"""
Exemple d'utilisation simple avec autotelemetry.

Cet exemple montre comment configurer facilement
toutes les fonctionnalités d'observabilité dans une application de traitement de données.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

# Ajouter le répertoire parent au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importer SimpleObservabilityClient pour avoir une instrumentation manuelle
from autotelemetry import SimpleObservabilityClient, LogLevel, Environment

# Initialisation du client d'observabilité
client = SimpleObservabilityClient(
    service_name="demo-auto-instrument",
    service_version="1.0.0",
    environment=Environment.DEVELOPMENT,
    prometheus_port=9092,  # Port différent pour éviter les conflits
    log_level=LogLevel.INFO
)

# Obtenir un logger
logger = client.get_logger()

def generate_data(rows=100):
    """Génère des données de test."""
    # Utilisation manuelle du logger
    logger.info(f"Génération de {rows} lignes de données")
    
    data = {
        'id': list(range(1, rows + 1)),
        'valeur': np.random.rand(rows) * 100,
        'categorie': np.random.choice(['A', 'B', 'C'], size=rows),
        'date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S") for _ in range(rows)]
    }
    df = pd.DataFrame(data)
    
    logger.info("Données générées avec succès", extra={"data": {
        "rows": len(df),
        "categories": df["categorie"].value_counts().to_dict()
    }})
    
    return df

def process_data(df):
    """Traite les données."""
    # Utilisation manuelle des traceurs
    with client.tracer.start_as_current_span("process_data"):
        original_len = len(df)
        
        # Filtrer valeurs > 50
        df_result = df[df.valeur <= 50].copy()
        
        # Grouper par catégorie
        result_stats = df_result.groupby('categorie').agg({
            'valeur': ['count', 'mean', 'sum']
        })
        
        # Logging avec données structurées
        logger.info("Données traitées", extra={"data": {
            "original_rows": original_len,
            "filtered_rows": len(df_result),
            "filter_ratio": len(df_result) / original_len
        }})
        
        return df_result, result_stats

def main():
    """Fonction principale."""
    logger.info("Démarrage du traitement")
    
    try:
        print("Génération des données...")
        df = generate_data(rows=1000)
        
        print(f"Données générées : {len(df)} lignes")
        
        print("Traitement des données...")
        result, stats = process_data(df)
        
        print(f"Données traitées : {len(result)} lignes")
        print("Statistiques par catégorie :")
        print(stats)
        
        logger.info("Traitement terminé avec succès")
        
    except Exception as e:
        # Logging d'erreur
        logger.error(f"Erreur lors du traitement: {str(e)}")
        print(f"Erreur : {str(e)}")
        raise
    finally:
        # Arrêt propre du client
        client.shutdown()

if __name__ == "__main__":
    main() 