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
from easy_telemetry import Telemetry
# Import supplémentaire pour le module trace
from opentelemetry import trace

# First, create a telemetry instance
telemetry = Telemetry(
    service_name="data-pipeline",
    service_version="1.0.0",
    environment="development"
)

# Then you can get loggers, tracers, and meters
logger = telemetry.get_logger()  # Will use "data-pipeline" as the name
tracer = telemetry.get_tracer()  # Will use "data-pipeline" as the name
meter = telemetry.get_meter()    # Will use "data-pipeline" as the name

# Create some metrics
processed_rows_counter = meter.create_counter(
    name="processed_rows_total",
    description="Total number of rows processed"
)

processing_time = meter.create_histogram(
    name="processing_time_seconds",
    description="Time taken to process data",
    unit="s"
)

saving_time = meter.create_histogram(
    name="save_time_seconds",
    description="Time taken to process data",
    unit="s"
)


def generate_sample_data(rows: int = 1000) -> pd.DataFrame:
    """Generate sample data for processing"""
    return pd.DataFrame({
        'value': np.random.normal(100, 15, rows),
        'category': np.random.choice(['A', 'B', 'C'], rows)
    })

def process_data(df: pd.DataFrame) -> Dict[str, float]:
    """Process the data and return statistics"""
    # Create a span for data processing step
    with tracer.start_as_current_span("process_data") as span:
        # Log the start of processing
        logger.info(f"Starting to process {len(df)} rows of data")
        
        # Record the start time for our histogram
        start_time = time.time()
        
        # Process the data
        result = {
            'mean': df['value'].mean(),
            'std': df['value'].std(),
            'categories': df['category'].nunique()
        }
        
        # Record metrics
        processed_rows_counter.add(len(df))
        processing_time.record(time.time() - start_time)
        
        # Log the results
        logger.info(f"Processing complete. Mean: {result['mean']:.2f}, Std: {result['std']:.2f}")
        
        return result

def save_data(df: pd.DataFrame, result: Dict[str, float]) -> None:
    """Save processed data and results"""
    with tracer.start_as_current_span("save_data") as span:
        logger.info("Starting to save data")
        start_time = time.time()

        # Simulate saving data
        time.sleep(0.5)
        # Record the start time for our histogram
        # Record metrics
        saving_time.record(time.time() - start_time)

        logger.info("Data saved successfully")

def main():
    # Log application startup
    
    try:
        # Process one batch - this is our pipeline
        with tracer.start_as_current_span("data_pipeline") as pipeline_span:

            logger.info("Starting data processing application")

            # Step 1: Generate data
            df = generate_sample_data(1000)
            
            # Step 2: Process data
            stats = process_data(df)
            
            # Step 3: Save data
            save_data(df, stats)
            
            logger.info("Pipeline completed successfully")
        
    except Exception as e:
        logger.error(f"Error during pipeline execution: {str(e)}")
        raise
    
    finally:
        logger.info("Shutting down data processing application")

main()