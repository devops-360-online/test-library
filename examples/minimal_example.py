#!/usr/bin/env python3
"""
Exemple minimal d'observabilité
-------------------------------

Cet exemple simple montre les concepts d'observabilité sans utiliser
la bibliothèque autotelemetry complète.
"""

import logging
import json
import time
import random
from datetime import datetime

# Configurer un logger simple avec format JSON
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Ajouter les données structurées si présentes
        if hasattr(record, 'data'):
            log_data["data"] = record.data
            
        # Ajouter les informations d'exception
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1])
            }
            
        return json.dumps(log_data)

# Configurer le logging
def setup_logging():
    logger = logging.getLogger("demo-observability")
    logger.setLevel(logging.INFO)
    
    # Supprimer les handlers existants
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Créer un handler console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JsonFormatter())
    logger.addHandler(console_handler)
    
    return logger

# Ajouter une méthode pour le logging structuré
def log_with_data(logger, level, message, data=None):
    if data is None:
        data = {}
    
    record = logging.LogRecord(
        name=logger.name,
        level=level,
        pathname="",
        lineno=0,
        msg=message,
        args=(),
        exc_info=None
    )
    record.data = data
    
    logger.handle(record)

# Classe de métriques simple
class SimpleMetrics:
    def __init__(self):
        self.counters = {}
        self.histograms = {}
    
    def increment_counter(self, name, value=1, labels=None):
        if name not in self.counters:
            self.counters[name] = 0
        self.counters[name] += value
        
        if labels:
            label_key = f"{name}_{json.dumps(labels, sort_keys=True)}"
            if label_key not in self.counters:
                self.counters[label_key] = 0
            self.counters[label_key] += value
    
    def record_histogram(self, name, value, labels=None):
        if name not in self.histograms:
            self.histograms[name] = []
        self.histograms[name].append(value)
        
        if labels:
            label_key = f"{name}_{json.dumps(labels, sort_keys=True)}"
            if label_key not in self.histograms:
                self.histograms[label_key] = []
            self.histograms[label_key].append(value)
    
    def get_metrics(self):
        return {
            "counters": self.counters,
            "histograms": {
                name: {
                    "count": len(values),
                    "sum": sum(values),
                    "avg": sum(values) / len(values) if values else 0,
                    "min": min(values) if values else 0,
                    "max": max(values) if values else 0
                }
                for name, values in self.histograms.items()
            }
        }

# Fonction simulant un traitement de données
def process_data(logger, metrics, items_count=100):
    log_with_data(logger, logging.INFO, "Démarrage du traitement", {
        "items_count": items_count,
        "timestamp": datetime.now().isoformat()
    })
    
    start_time = time.time()
    
    # Simuler un traitement
    processed = 0
    errors = 0
    
    for i in range(items_count):
        try:
            # Simuler une latence
            processing_time = random.uniform(0.001, 0.01)
            time.sleep(processing_time)
            
            # Métriques sur la latence
            metrics.record_histogram("processing_time_ms", processing_time * 1000, {
                "batch": f"batch_{i // 10}"
            })
            
            # Simuler des erreurs aléatoires
            if random.random() < 0.05:
                raise ValueError(f"Erreur simulée à l'index {i}")
                
            processed += 1
            
            # Incrémenter les compteurs
            metrics.increment_counter("items_processed", 1, {
                "success": True
            })
            
        except Exception as e:
            # Logging des erreurs
            log_with_data(logger, logging.ERROR, f"Erreur de traitement: {str(e)}", {
                "index": i,
                "error_type": type(e).__name__
            })
            
            errors += 1
            metrics.increment_counter("items_processed", 1, {
                "success": False
            })
    
    # Calculer le temps total
    total_time = time.time() - start_time
    metrics.record_histogram("total_processing_time_ms", total_time * 1000)
    
    # Log de fin de traitement
    log_with_data(logger, logging.INFO, "Traitement terminé", {
        "processed": processed,
        "errors": errors,
        "total_time_ms": total_time * 1000,
        "items_per_second": items_count / total_time if total_time > 0 else 0
    })
    
    return processed, errors

# Fonction principale
def main():
    # Configuration
    logger = setup_logging()
    metrics = SimpleMetrics()
    
    logger.info("Démarrage de l'exemple d'observabilité")
    
    try:
        # Traiter les données
        processed, errors = process_data(logger, metrics, items_count=50)
        
        # Afficher les métriques collectées
        log_with_data(logger, logging.INFO, "Métriques collectées", {
            "metrics": metrics.get_metrics()
        })
        
    except Exception as e:
        logger.exception(f"Erreur dans l'exécution: {str(e)}")
    
    logger.info("Fin de l'exemple")

if __name__ == "__main__":
    main() 