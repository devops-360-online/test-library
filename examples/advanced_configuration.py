#!/usr/bin/env python3
"""
Exemple de configuration avancée de l'auto-instrumentation avec autotelemetry.

Cet exemple montre comment configurer de manière avancée l'auto-instrumentation
pour des besoins personnalisés tout en conservant les logs JSON standardisés.
"""

import logging
import pandas as pd
import numpy as np
import time

# Import de la bibliothèque avec configuration avancée
from autotelemetry import auto_instrument, LogLevel, Environment

# Configuration avancée de l'auto-instrumentation
client = auto_instrument(
    service_name="demo-advanced",
    service_version="1.0.0",
    environment=Environment.DEVELOPMENT,
    prometheus_port=9090,
    log_level=LogLevel.DEBUG,
    additional_attributes={
        "team": "data-engineering",
        "component": "etl-pipeline"
    },
    enable_console_export=True,
    # Le format JSON est obligatoire en production, mais peut être désactivé en développement
    # pour une meilleure lisibilité dans la console
    json_logs=False  # Format texte uniquement en développement pour lisibilité
)

# Obtenir un logger personnalisé
logger = client.get_logger()

def simulate_data_pipeline():
    """Simule un pipeline de données complet."""
    try:
        logger.info("Démarrage du pipeline de données", extra={"pipeline_id": "demo-123"})
        
        # Étape 1: Extraction
        data = extract_data()
        
        # Étape 2: Transformation
        transformed_data = transform_data(data)
        
        # Étape 3: Chargement
        load_data(transformed_data)
        
        logger.info("Pipeline terminé avec succès")
        return "Pipeline exécuté avec succès"
    except Exception as e:
        # Automatiquement loggé avec le contexte complet
        logger.error(f"Erreur dans le pipeline: {str(e)}")
        raise

def extract_data():
    """Extrait des données d'une source simulée."""
    # Simuler un temps de traitement
    time.sleep(0.5)
    
    # Créer des données synthétiques
    data = pd.DataFrame({
        'id': range(1, 101),
        'valeur': np.random.normal(50, 15, 100),
        'categorie': np.random.choice(['X', 'Y', 'Z'], size=100)
    })
    
    # En production, ce log serait automatiquement structuré en JSON
    logger.info(f"Données extraites: {len(data)} lignes", 
               extra={"rows_count": len(data), "stage": "extract"})
    return data

def transform_data(df):
    """Applique des transformations aux données."""
    # Simuler un temps de traitement
    time.sleep(0.7)
    
    # Normaliser les valeurs
    df['valeur_normalisee'] = (df['valeur'] - df['valeur'].mean()) / df['valeur'].std()
    
    # Ajouter une colonne calculée
    df['valeur_carre'] = df['valeur'] ** 2
    
    # Filtrer les valeurs aberrantes
    df_clean = df[df['valeur_normalisee'].abs() < 2].copy()
    
    removed_count = len(df) - len(df_clean)
    
    # Logging structuré avec contexte enrichi
    with logger.with_data(stage="transform", operation="filter_outliers"):
        logger.data(
            level=logging.INFO,
            msg=f"Données transformées: {len(df_clean)} lignes",
            data={
                "input_rows": len(df),
                "output_rows": len(df_clean),
                "removed_rows": removed_count,
                "removal_ratio": removed_count / len(df) if len(df) > 0 else 0
            }
        )
    
    return df_clean

def load_data(df):
    """Charge les données dans une destination simulée."""
    # Simuler un temps de traitement
    time.sleep(0.3)
    
    # Simuler une sauvegarde
    grouped = df.groupby('categorie').agg({
        'valeur': ['count', 'mean', 'std'],
        'valeur_carre': ['sum', 'mean']
    })
    
    # En production, ce serait automatiquement formaté en JSON
    logger.info("Données chargées avec succès", 
               extra={"categories_count": len(grouped), "stage": "load"})
    
    return True

if __name__ == "__main__":
    # Le démarrage est automatiquement loggé
    result = simulate_data_pipeline()
    print(result)
    
    # En environnement de production, vous verriez ici tous les logs en format JSON standardisé
    # avec des champs cohérents pour faciliter l'analyse et la recherche 