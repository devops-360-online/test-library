#!/usr/bin/env python3
"""
Exemple simple d'utilisation de simple_observability.

Cet exemple montre comment une seule ligne de code active automatiquement
toutes les fonctionnalités d'observabilité.
"""

import time
import pandas as pd
import numpy as np
from datetime import datetime

# Une seule ligne pour activer toute l'observabilité
from simple_observability import auto_instrument
auto_instrument(service_name="demo-simple")

def generate_data(rows=100):
    """Génère des données de test."""
    # Les métriques, logs et traces sont automatiquement collectés
    data = {
        'id': list(range(1, rows + 1)),
        'valeur': np.random.rand(rows) * 100,
        'categorie': np.random.choice(['A', 'B', 'C'], size=rows),
        'date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S") for _ in range(rows)]
    }
    return pd.DataFrame(data)

def process_data(df):
    """Traite les données."""
    # Les performances et métriques sont automatiquement mesurés
    start_time = time.time()
    
    # Simuler un traitement - filtrer valeurs > 50
    original_len = len(df)
    df_result = df[df.valeur <= 50].copy()
    filtered_count = original_len - len(df_result)
    
    # Les métriques de performance sont automatiquement collectées
    return df_result

def main():
    """Fonction principale."""
    try:
        # Chaque étape est automatiquement tracée
        df = generate_data(rows=1000)
        result = process_data(df)
        
        # Les statistiques sont automatiquement collectées
        categories = result.categorie.value_counts().to_dict()
        
    except Exception as e:
        # Les erreurs sont automatiquement loggées avec contexte
        raise

if __name__ == "__main__":
    main() 