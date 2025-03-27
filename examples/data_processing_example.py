#!/usr/bin/env python3
"""
Exemple d'instrumentation automatique des données avec AutoTelemetry
-------------------------------------------------------------------

Cet exemple montre comment AutoTelemetry capture automatiquement les métriques 
de données traitées (nombre de lignes, taille, temps de traitement, etc.)
"""

import os
import sys
import time
import random
import pandas as pd
import numpy as np

# Ajouter le répertoire parent au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importer AutoTelemetry
from autotelemetry import auto_instrument

# Initialiser AutoTelemetry avec auto-instrumentation
client = auto_instrument(
    service_name="demo-data-metrics",
    service_version="1.0.0",
    prometheus_port=9093  # Port différent pour éviter les conflits
)

# Obtenir un logger
logger = client.get_logger()

def generate_large_dataframe(rows=10000, cols=10):
    """Génère un grand DataFrame pour démonstration."""
    logger.info(f"Génération d'un DataFrame de {rows} lignes et {cols} colonnes")
    
    data = {}
    
    # Créer des colonnes numériques
    for i in range(cols):
        if i % 3 == 0:
            # Colonne normale
            data[f'numeric_{i}'] = np.random.normal(100, 15, rows)
        elif i % 3 == 1:
            # Colonne uniforme
            data[f'uniform_{i}'] = np.random.uniform(0, 100, rows)
        else:
            # Colonne exponentielle
            data[f'exp_{i}'] = np.random.exponential(5, rows)
    
    # Ajouter une colonne catégorielle
    categories = ['A', 'B', 'C', 'D', 'E']
    data['category'] = np.random.choice(categories, rows)
    
    # Ajouter une colonne temporelle
    data['timestamp'] = pd.date_range(start='2024-01-01', periods=rows, freq='1min')
    
    # Créer le DataFrame
    df = pd.DataFrame(data)
    
    logger.info(f"DataFrame généré avec succès: {df.shape[0]} lignes, {df.shape[1]} colonnes")
    
    # Ajouter des valeurs NaN aléatoirement (1%)
    mask = np.random.random(df.shape) < 0.01
    df.mask(mask, np.nan, inplace=True)
    
    logger.info(f"Mémoire utilisée par le DataFrame: {df.memory_usage(deep=True).sum() / (1024*1024):.2f} MB")
    
    return df

def process_dataframe(df):
    """Traite le DataFrame avec diverses opérations."""
    # Commencer par filtrer les valeurs NaN
    logger.info("Filtrage des valeurs NaN...")
    df_clean = df.dropna()
    
    logger.info(f"Après filtrage: {len(df_clean)} lignes (supprimé {len(df) - len(df_clean)} lignes)")
    
    # Effectuer quelques calculs de base
    logger.info("Calcul des statistiques de base...")
    stats = {}
    
    # Sélectionner uniquement les colonnes numériques
    numeric_cols = df_clean.select_dtypes(include=['float64', 'int64']).columns
    
    for col in numeric_cols:
        # Ces opérations NumPy seront automatiquement instrumentées
        stats[col] = {
            'mean': np.mean(df_clean[col]),
            'median': np.median(df_clean[col]),
            'std': np.std(df_clean[col]),
            'min': np.min(df_clean[col]),
            'max': np.max(df_clean[col])
        }
    
    # Grouper par catégorie
    logger.info("Groupement par catégorie...")
    # Cette opération Pandas sera automatiquement instrumentée
    grouped = df_clean.groupby('category')[numeric_cols].agg(['mean', 'count'])
    
    # Filtrer les valeurs extrêmes (>2 écarts-types de la moyenne)
    logger.info("Filtrage des valeurs extrêmes...")
    filtered_df = df_clean.copy()
    
    for col in numeric_cols:
        mean = stats[col]['mean']
        std = stats[col]['std']
        upper_bound = mean + 2 * std
        lower_bound = mean - 2 * std
        
        # Filtrer le DataFrame
        mask = (filtered_df[col] >= lower_bound) & (filtered_df[col] <= upper_bound)
        filtered_df = filtered_df[mask]
    
    logger.info(f"Après filtrage des valeurs extrêmes: {len(filtered_df)} lignes")
    
    # Effectuer une jointure pour démonstration
    logger.info("Préparation d'une jointure...")
    
    # Créer un petit DataFrame de référence
    categories_df = pd.DataFrame({
        'category': ['A', 'B', 'C', 'D', 'E'],
        'category_name': ['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon'],
        'priority': [1, 2, 3, 2, 1]
    })
    
    # Effectuer la jointure
    logger.info("Exécution de la jointure...")
    # Cette opération Pandas sera automatiquement instrumentée
    result_df = pd.merge(filtered_df, categories_df, on='category', how='left')
    
    logger.info(f"Résultat final: {len(result_df)} lignes, {result_df.shape[1]} colonnes")
    
    return result_df, stats, grouped

def main():
    """Fonction principale."""
    try:
        logger.info("Démarrage de l'exemple d'instrumentation des données")
        
        # Générer les données
        df = generate_large_dataframe(rows=50000, cols=8)
        
        # Traiter les données
        start_time = time.time()
        result, stats, grouped = process_dataframe(df)
        processing_time = time.time() - start_time
        
        logger.info(f"Traitement terminé en {processing_time:.2f} secondes")
        
        # Afficher quelques résultats
        print(f"\nStatistiques par catégorie:\n{'-'*30}")
        print(grouped.head())
        
        print(f"\nRésumé du traitement:\n{'-'*30}")
        print(f"Lignes brutes: {len(df)}")
        print(f"Lignes finales: {len(result)}")
        print(f"Colonnes: {result.shape[1]}")
        print(f"Temps de traitement: {processing_time:.2f} secondes")
        
        # Toutes ces opérations ont généré des métriques automatiquement!
        logger.info("Exemple terminé. Consultez les métriques Prometheus sur le port 9093.")
        
    except Exception as e:
        logger.error(f"Erreur pendant l'exécution: {str(e)}")
        raise
    finally:
        logger.info("Arrêt du client d'observabilité")
        client.shutdown()

if __name__ == "__main__":
    main() 