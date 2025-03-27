#!/usr/bin/env python3
"""
Exemple d'utilisation de Mini-Telemetry dans un contexte de traitement de données
"""

import pandas as pd
import numpy as np
import time
import random
from typing import Dict, List, Tuple, Optional

# Import de la bibliothèque Mini-Telemetry
from mini_telemetry import TelemetryTools
# Import supplémentaire pour le module trace
from opentelemetry import trace

# Initialisation de la télémétrie
telemetry = TelemetryTools(
    service_name="data-pipeline",
    service_version="1.0.0",
    environment="development",
    use_json_logs=True  # Format JSON pour les logs
)

# Obtenir les outils pour différents composants
extract_tracer = telemetry.get_tracer("data.extract")
transform_tracer = telemetry.get_tracer("data.transform")
load_tracer = telemetry.get_tracer("data.load")

# Logger principal
logger = telemetry.get_logger("data.pipeline")

# Métriques pour le pipeline de données
meter = telemetry.get_meter("data.metrics")

# Création des métriques
rows_processed = meter.create_counter(
    name="data.rows.processed",
    description="Nombre de lignes traitées",
    unit="1"
)

data_quality_score = meter.create_histogram(
    name="data.quality.score",
    description="Score de qualité des données",
    unit="1"
)

processing_time = meter.create_histogram(
    name="data.processing.duration",
    description="Temps de traitement des données",
    unit="ms"
)

# Fonction d'extraction des données
def extract_data(source: str, sample_size: Optional[int] = None) -> pd.DataFrame:
    """
    Extrait les données depuis une source (simulée)
    
    Args:
        source: Identifiant de la source de données
        sample_size: Taille de l'échantillon à extraire (None = tout)
        
    Returns:
        DataFrame contenant les données extraites
    """
    with extract_tracer.start_as_current_span("extract_data") as span:
        start_time = time.time()
        
        # Ajout d'attributs au span pour le contexte
        span.set_attribute("data.source", source)
        span.set_attribute("data.sample_size", sample_size if sample_size else -1)
        
        logger.info(f"Extraction des données depuis {source} démarrée")
        
        try:
            # Simuler l'extraction de données
            # Dans un cas réel, ce serait une lecture depuis une BD, un fichier, une API, etc.
            with extract_tracer.start_as_current_span("generate_synthetic_data"):
                time.sleep(0.2)  # Simuler le temps d'accès
                
                # Générer des données synthétiques
                n_rows = sample_size if sample_size else random.randint(500, 1000)
                data = {
                    'id': range(1, n_rows + 1),
                    'value_a': np.random.normal(100, 15, n_rows),
                    'value_b': np.random.normal(50, 5, n_rows),
                    'category': np.random.choice(['A', 'B', 'C', 'D'], n_rows),
                    'timestamp': pd.date_range(start='2023-01-01', periods=n_rows, freq='H')
                }
                
                df = pd.DataFrame(data)
                
                # Ajouter quelques valeurs manquantes pour simuler des problèmes de qualité
                mask = np.random.random(n_rows) < 0.05
                df.loc[mask, 'value_a'] = np.nan
                
                # Ajouter quelques valeurs aberrantes
                outlier_mask = np.random.random(n_rows) < 0.02
                df.loc[outlier_mask, 'value_b'] = np.random.normal(200, 20, sum(outlier_mask))
            
            # Enregistrer des métriques sur l'extraction
            rows_processed.add(len(df), {"operation": "extract", "source": source})
            
            logger.info(f"Extraction terminée: {len(df)} lignes extraites de {source}")
            span.set_attribute("data.rows_extracted", len(df))
            
            # Stocker le nombre de lignes dans le contexte pour référence ultérieure
            telemetry.set_context_data("rows_extracted", len(df))
            
            return df
            
        except Exception as e:
            error_msg = f"Erreur lors de l'extraction depuis {source}: {str(e)}"
            logger.error(error_msg)
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, error_msg))
            raise
        
        finally:
            duration_ms = (time.time() - start_time) * 1000
            processing_time.record(duration_ms, {"operation": "extract", "source": source})
            logger.info(f"Opération d'extraction terminée en {duration_ms:.2f} ms")

# Fonction d'évaluation de la qualité des données
def evaluate_data_quality(df: pd.DataFrame) -> Dict[str, float]:
    """
    Évalue la qualité des données et renvoie des métriques
    
    Args:
        df: DataFrame à évaluer
        
    Returns:
        Dictionnaire de scores de qualité
    """
    with transform_tracer.start_as_current_span("evaluate_data_quality") as span:
        span.set_attribute("data.columns", ",".join(df.columns))
        span.set_attribute("data.rows", len(df))
        
        # Calculer différentes métriques de qualité
        quality_metrics = {}
        
        # 1. Complétude (pourcentage de valeurs non-nulles)
        completeness = 100 * (1 - df.isnull().mean())
        quality_metrics["completeness"] = completeness.mean()
        
        # 2. Unicité des identifiants
        uniqueness = 100 * (df['id'].nunique() / len(df))
        quality_metrics["uniqueness"] = uniqueness
        
        # 3. Détection de valeurs aberrantes (pour value_b)
        # Utiliser l'écart interquartile (IQR) pour définir les limites
        q1 = df['value_b'].quantile(0.25)
        q3 = df['value_b'].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = df[(df['value_b'] < lower_bound) | (df['value_b'] > upper_bound)]
        outlier_rate = 100 * len(outliers) / len(df)
        quality_metrics["outlier_rate"] = outlier_rate
        
        # 4. Score global (moyenne pondérée)
        global_score = (
            0.4 * quality_metrics["completeness"] + 
            0.3 * quality_metrics["uniqueness"] + 
            0.3 * (100 - quality_metrics["outlier_rate"])
        )
        quality_metrics["global_score"] = global_score
        
        # Enregistrer les métriques de qualité
        for metric_name, metric_value in quality_metrics.items():
            span.set_attribute(f"quality.{metric_name}", metric_value)
            
        data_quality_score.record(global_score, {"data_set": "main"})
        
        # Stocker les métriques dans le contexte
        telemetry.set_context_data("quality_metrics", quality_metrics)
        
        # Journaliser les résultats
        logger.info(f"Évaluation de qualité: score global de {global_score:.2f}/100")
        for metric_name, metric_value in quality_metrics.items():
            if metric_name != "global_score":
                logger.debug(f"Métrique de qualité - {metric_name}: {metric_value:.2f}%")
        
        return quality_metrics

# Fonction de transformation des données
def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie et transforme les données
    
    Args:
        df: DataFrame à transformer
        
    Returns:
        DataFrame transformé
    """
    with transform_tracer.start_as_current_span("transform_data") as span:
        start_time = time.time()
        span.set_attribute("data.input_rows", len(df))
        
        logger.info("Transformation des données démarrée")
        
        try:
            # 1. Évaluer la qualité avant transformation
            quality_before = evaluate_data_quality(df)
            
            # 2. Nettoyer les données
            with transform_tracer.start_as_current_span("clean_data"):
                # Remplir les valeurs manquantes
                df['value_a'] = df['value_a'].fillna(df['value_a'].mean())
                
                # Éliminer les valeurs aberrantes
                q1 = df['value_b'].quantile(0.25)
                q3 = df['value_b'].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                # Remplacer les valeurs aberrantes par les limites
                df.loc[df['value_b'] < lower_bound, 'value_b'] = lower_bound
                df.loc[df['value_b'] > upper_bound, 'value_b'] = upper_bound
            
            # 3. Ajouter des caractéristiques
            with transform_tracer.start_as_current_span("feature_engineering"):
                # Créer une nouvelle colonne calculée
                df['ratio'] = df['value_a'] / df['value_b']
                
                # Extraire des composantes temporelles
                df['hour'] = df['timestamp'].dt.hour
                df['day_of_week'] = df['timestamp'].dt.dayofweek
                
                # Créer une variable catégorielle encodée
                df = pd.get_dummies(df, columns=['category'], prefix='cat')
            
            # 4. Évaluer la qualité après transformation
            quality_after = evaluate_data_quality(df)
            
            # Calculer l'amélioration de la qualité
            quality_improvement = quality_after["global_score"] - quality_before["global_score"]
            span.set_attribute("quality.improvement", quality_improvement)
            
            if quality_improvement > 0:
                logger.info(f"Amélioration de la qualité: +{quality_improvement:.2f} points")
            else:
                logger.warning(f"Pas d'amélioration de qualité: {quality_improvement:.2f} points")
            
            # Enregistrer des métriques sur les transformations
            rows_processed.add(len(df), {"operation": "transform"})
            
            logger.info(f"Transformation terminée: {len(df)} lignes, {len(df.columns)} colonnes")
            span.set_attribute("data.output_rows", len(df))
            span.set_attribute("data.output_columns", len(df.columns))
            
            return df
            
        except Exception as e:
            error_msg = f"Erreur lors de la transformation: {str(e)}"
            logger.error(error_msg)
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, error_msg))
            raise
        
        finally:
            duration_ms = (time.time() - start_time) * 1000
            processing_time.record(duration_ms, {"operation": "transform"})
            logger.info(f"Opération de transformation terminée en {duration_ms:.2f} ms")

# Fonction de chargement des données
def load_data(df: pd.DataFrame, destination: str) -> bool:
    """
    Charge les données transformées vers une destination (simulée)
    
    Args:
        df: DataFrame à charger
        destination: Identifiant de la destination
        
    Returns:
        True si le chargement a réussi
    """
    with load_tracer.start_as_current_span("load_data") as span:
        start_time = time.time()
        
        # Ajout d'attributs au span pour le contexte
        span.set_attribute("data.destination", destination)
        span.set_attribute("data.rows", len(df))
        span.set_attribute("data.columns", len(df.columns))
        
        logger.info(f"Chargement des données vers {destination} démarré")
        
        try:
            # Simuler le chargement des données
            # Dans un cas réel, ce serait une écriture dans une BD, un fichier, une API, etc.
            with load_tracer.start_as_current_span("write_to_destination"):
                # Simuler le temps d'écriture (proportionnel à la taille des données)
                time_factor = len(df) * len(df.columns) / 5000
                time.sleep(0.1 + time_factor)
                
                # Simuler un échec occasionnel pour montrer la gestion d'erreur
                if random.random() < 0.1:  # 10% de chance d'échec
                    raise IOError(f"Échec de connexion à {destination}")
            
            # Enregistrer des métriques sur le chargement
            rows_processed.add(len(df), {"operation": "load", "destination": destination})
            
            # Récupérer le nombre de lignes extraites du contexte pour calculer le ratio
            rows_extracted = telemetry.get_context_data("rows_extracted", 0)
            if rows_extracted > 0:
                processing_ratio = len(df) / rows_extracted
                span.set_attribute("data.processing_ratio", processing_ratio)
                logger.info(f"Ratio de lignes chargées/extraites: {processing_ratio:.2f}")
            
            logger.info(f"Chargement terminé: {len(df)} lignes chargées vers {destination}")
            
            return True
            
        except Exception as e:
            error_msg = f"Erreur lors du chargement vers {destination}: {str(e)}"
            logger.error(error_msg)
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, error_msg))
            return False
        
        finally:
            duration_ms = (time.time() - start_time) * 1000
            processing_time.record(duration_ms, {"operation": "load", "destination": destination})
            logger.info(f"Opération de chargement terminée en {duration_ms:.2f} ms")

# Fonction principale d'exécution du pipeline
def run_data_pipeline(source: str, destination: str, sample_size: Optional[int] = None):
    """
    Exécute le pipeline ETL complet
    
    Args:
        source: Source des données
        destination: Destination des données
        sample_size: Taille optionnelle de l'échantillon
    """
    pipeline_start = time.time()
    logger.info(f"Démarrage du pipeline de données {source} -> {destination}")
    
    # Stockage des métadonnées du pipeline dans le contexte
    telemetry.update_context_data({
        "pipeline_source": source,
        "pipeline_destination": destination,
        "pipeline_start_time": pipeline_start,
        "sample_size": sample_size
    })
    
    try:
        # 1. Extraction
        df_raw = extract_data(source, sample_size)
        
        # 2. Transformation
        df_transformed = transform_data(df_raw)
        
        # 3. Chargement
        success = load_data(df_transformed, destination)
        
        # Résumé du pipeline
        pipeline_duration = (time.time() - pipeline_start) * 1000
        
        if success:
            logger.info(f"Pipeline terminé avec succès en {pipeline_duration:.2f} ms")
            
            # Récupérer les métriques de qualité du contexte
            quality_metrics = telemetry.get_context_data("quality_metrics", {})
            global_score = quality_metrics.get("global_score", 0)
            
            # Journaliser un résumé structuré
            summary = {
                "pipeline_status": "success",
                "duration_ms": pipeline_duration,
                "rows_processed": len(df_transformed),
                "quality_score": global_score,
                "source": source,
                "destination": destination
            }
            logger.info("Résumé du pipeline", extra={"pipeline_summary": summary})
        else:
            logger.error(f"Pipeline terminé avec erreur en {pipeline_duration:.2f} ms")
    
    except Exception as e:
        pipeline_duration = (time.time() - pipeline_start) * 1000
        logger.error(f"Échec du pipeline: {str(e)}")
        logger.error(f"Pipeline terminé avec exception en {pipeline_duration:.2f} ms")
    
    finally:
        # Nettoyer le contexte pour le prochain pipeline
        telemetry.clear_context_data()

# Exécution du script principal
if __name__ == "__main__":
    print("\n=== DÉMARRAGE DU PIPELINE DE DONNÉES AVEC MINI-TELEMETRY ===")
    print("Toutes les données d'observabilité sont exportées vers stdout")
    print("Aucun composant externe n'est nécessaire\n")
    
    # Exécuter le pipeline sur différentes sources
    sources = ["database", "api", "file"]
    destinations = ["data_warehouse", "analytics_db", "reporting_tool"]
    
    for i, (source, destination) in enumerate(zip(sources, destinations)):
        print(f"\n--- Exécution du pipeline {i+1}/{len(sources)}: {source} -> {destination} ---")
        run_data_pipeline(source, destination, sample_size=random.randint(200, 500))
        time.sleep(1)  # Pause entre les pipelines
    
    print("\n=== PIPELINES TERMINÉS ===")
    print("Toutes les traces, logs et métriques ont été affichés dans la console") 