#!/usr/bin/env python3
"""
Exemple d'utilisation de l'auto-instrumentation avec simple_observability.

Cet exemple montre comment une seule ligne de code active automatiquement
toutes les fonctionnalités d'observabilité dans une application de traitement de données.
"""

import pandas as pd
import numpy as np
from datetime import datetime

# Une seule ligne pour activer toute l'observabilité
from simple_observability import auto_instrument
auto_instrument(service_name="demo-auto-instrument")

def generate_data(rows=100):
    """Génère des données de test."""
    # Automatiquement tracé
    data = {
        'id': list(range(1, rows + 1)),
        'valeur': np.random.rand(rows) * 100,
        'categorie': np.random.choice(['A', 'B', 'C'], size=rows),
        'date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S") for _ in range(rows)]
    }
    return pd.DataFrame(data)

def process_data(df):
    """Traite les données."""
    # Automatiquement tracé avec métriques
    original_len = len(df)
    
    # Filtrer valeurs > 50
    df_result = df[df.valeur <= 50].copy()
    
    # Grouper par catégorie
    result_stats = df_result.groupby('categorie').agg({
        'valeur': ['count', 'mean', 'sum']
    })
    
    return df_result, result_stats

def main():
    """Fonction principale."""
    # Auto-instrumenté - toutes les étapes sont tracées
    try:
        print("Génération des données...")
        df = generate_data(rows=1000)
        
        print(f"Données générées : {len(df)} lignes")
        
        print("Traitement des données...")
        result, stats = process_data(df)
        
        print(f"Données traitées : {len(result)} lignes")
        print("Statistiques par catégorie :")
        print(stats)
        
    except Exception as e:
        # Automatiquement loggé avec contexte de trace
        print(f"Erreur : {str(e)}")
        raise

if __name__ == "__main__":
    main() 