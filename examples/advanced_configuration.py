#!/usr/bin/env python3
"""
Exemple de configuration avancée de l'auto-instrumentation avec simple_observability.

Cet exemple montre comment configurer de manière avancée l'auto-instrumentation
pour des besoins personnalisés.
"""

import logging
import pandas as pd
import numpy as np
import time

# Import de la bibliothèque avec configuration avancée
from simple_observability import auto_instrument, LogLevel

# Configuration avancée de l'auto-instrumentation
client = auto_instrument(
    service_name="demo-advanced",
    service_version="1.0.0",
    environment="development",
    prometheus_port=9090,
    log_level=LogLevel.DEBUG,
    additional_attributes={
        "team": "data-engineering",
        "component": "etl-pipeline"
    },
    enable_console_export=True,
    json_logs=False
)

def simulate_data_pipeline():
    """Simule un pipeline de données complet."""
    try:
        # Étape 1: Extraction
        data = extract_data()
        
        # Étape 2: Transformation
        transformed_data = transform_data(data)
        
        # Étape 3: Chargement
        load_data(transformed_data)
        
        return "Pipeline exécuté avec succès"
    except Exception as e:
        # Automatiquement loggé avec le contexte complet
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
    
    print(f"Données extraites: {len(data)} lignes")
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
    
    print(f"Données transformées: {len(df_clean)} lignes (supprimées: {len(df) - len(df_clean)})")
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
    
    print("Résumé des données chargées:")
    print(grouped)
    
    return True

if __name__ == "__main__":
    result = simulate_data_pipeline()
    print(result) 