#!/usr/bin/env python3
"""
Exemple simple d'utilisation de simple_observability.

Cet exemple montre l'initialisation basique et l'usage des fonctionnalités principales.
"""

import time
import logging
import pandas as pd
import numpy as np
from datetime import datetime

# Import de la bibliothèque
from simple_observability import ObservabilityClient

# Initialisation avec seulement le nom du service
# Toutes les autres options utiliseront les valeurs par défaut
obs = ObservabilityClient(service_name="demo-simple")

# Obtenir un logger
logger = obs.get_logger()

# Fonction tracée automatiquement avec le décorateur
@obs.trace_data_processing()
def generate_data(rows=100):
    """Génère des données de test."""
    logger.info(f"Génération de {rows} lignes de données")
    
    # Créer des données synthétiques
    data = {
        'id': list(range(1, rows + 1)),
        'valeur': np.random.rand(rows) * 100,
        'categorie': np.random.choice(['A', 'B', 'C'], size=rows),
        'date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S") for _ in range(rows)]
    }
    
    return pd.DataFrame(data)

# Fonction tracée qui utilise des métriques
def process_data(df, metrics):
    """Traite les données et enregistre des métriques."""
    
    # Utiliser le gestionnaire de contexte d'opération standardisé
    with obs.data_operation("clean", "test_dataframe") as span:
        start_time = time.time()
        
        # Simuler un traitement - filtrer valeurs > 50
        original_len = len(df)
        df_result = df[df.valeur <= 50].copy()
        filtered_count = original_len - len(df_result)
        
        # Ajouter attributs à la span
        span.set_attribute("rows.original", original_len)
        span.set_attribute("rows.filtered", filtered_count)
        
        # Enregistrer des métriques
        metrics["rows_processed"].add(original_len)
        metrics["processing_duration"].record(time.time() - start_time)
        
        # Log structuré avec contexte
        logger.data(
            level=logging.INFO,
            msg=f"Filtrage terminé: {filtered_count} lignes supprimées",
            data={
                "filtered_ratio": filtered_count / original_len,
                "remaining_rows": len(df_result)
            }
        )
        
        return df_result

def main():
    """Fonction principale."""
    logger.info("Démarrage de l'exemple simple")
    
    # Créer des métriques standardisées pour le traitement de données
    metrics = obs.create_data_processing_metrics(prefix="demo")
    
    # Utiliser un contexte de tâche chronométrée
    with obs.timed_task("demo_workflow", {"example": "simple"}) as ctx:
        try:
            # Générer des données
            df = generate_data(rows=1000)
            
            # Traiter les données
            result = process_data(df, metrics)
            
            # Log du résultat
            categories = result.categorie.value_counts().to_dict()
            
            # Log structuré des statistiques finales
            with logger.with_data(stats=categories):
                logger.info(f"Traitement terminé avec succès: {len(result)} lignes restantes")
                
        except Exception as e:
            logger.exception(f"Erreur dans le workflow: {str(e)}")
    
    logger.info("Exemple terminé")

if __name__ == "__main__":
    main()
    
    # Fermeture propre (optionnel, fait automatiquement par atexit)
    obs.shutdown() 