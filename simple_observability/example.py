#!/usr/bin/env python3
"""
Example usage of the simple_observability library.

This script demonstrates how to use the observability library
for a typical data processing workflow.
"""

import logging
import time
import random
import numpy as np
import pandas as pd
from typing import List, Dict, Any

# Import our observability client
from .observability import ObservabilityClient

# Initialize the observability client
obs = ObservabilityClient(
    service_name="example-data-script",
    service_version="0.1.0",
    environment="development",
    # These parameters are optional and have defaults
    prometheus_port=8000,
    log_level=logging.INFO,
    enable_console_export=True
)

# Get a logger
logger = obs.get_logger()


# Use the trace_function decorator to automatically trace this function
@obs.trace_function(attributes={"function_type": "data_generation"})
def generate_sample_data(rows: int, columns: int) -> pd.DataFrame:
    """Generate sample data for demonstration purposes."""
    logger.info(f"Generating sample data with {rows} rows and {columns} columns")
    
    # Create a simple dataframe with random data
    data = {}
    for i in range(columns):
        data[f"feature_{i}"] = np.random.randn(rows)
    
    # Add some missing values
    for col in data:
        mask = np.random.choice([True, False], size=rows, p=[0.05, 0.95])
        data[col] = [np.nan if m else v for m, v in zip(mask, data[col])]
    
    return pd.DataFrame(data)


# Use the specialized data processing decorator
@obs.trace_data_processing(attributes={"operation": "clean_data"})
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the data by removing missing values."""
    logger.info(f"Cleaning data with {df.shape[0]} rows")
    
    # Simulate some processing time
    time.sleep(random.uniform(0.1, 0.3))
    
    # Count missing values before cleaning
    missing_count = df.isna().sum().sum()
    logger.info(f"Found {missing_count} missing values")
    
    # Clean the data
    result = df.dropna()
    
    # Count rows after cleaning
    rows_removed = df.shape[0] - result.shape[0]
    logger.info(f"Removed {rows_removed} rows with missing values")
    
    return result


@obs.trace_data_processing(attributes={"operation": "transform_data"})
def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply some transformations to the data."""
    logger.info(f"Transforming {df.shape[0]} rows of data")
    
    # Simulate some processing time
    time.sleep(random.uniform(0.2, 0.5))
    
    # Apply a simple transformation (standardize the data)
    for col in df.columns:
        df[col] = (df[col] - df[col].mean()) / df[col].std()
    
    logger.info(f"Transformation complete")
    return df


def main():
    """Main function demonstrating the observability features."""
    logger.info("Starting data processing example")
    
    # Create standard metrics for data processing
    metrics = obs.create_data_processing_metrics(prefix="example")
    
    # Use the high-level timed_task context manager
    with obs.timed_task("complete_data_workflow", {"demo": "true"}) as ctx:
        try:
            # Generate sample data
            df = generate_sample_data(1000, 5)
            metrics["rows_processed"].add(len(df))
            
            # Record batch size
            metrics["batch_size"].record(len(df))
            
            # Track memory usage (very simplified)
            memory_usage = df.memory_usage(deep=True).sum()
            metrics["memory_usage"].add(memory_usage)
            
            # Process the data
            start_time = time.time()
            df_clean = clean_data(df)
            df_transformed = transform_data(df_clean)
            processing_time = time.time() - start_time
            
            # Record processing time
            metrics["processing_duration"].record(processing_time)
            
            # Log some results
            logger.info(f"Processing complete! Final data shape: {df_transformed.shape}")
            
            # Simulate an error sometimes to demonstrate error tracking
            if random.random() < 0.2:
                raise ValueError("Random error for demonstration purposes")
                
        except Exception as e:
            logger.error(f"Error in data processing: {str(e)}")
            metrics["processing_errors"].add(1)
            raise


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception("Application error")
    finally:
        # Ensure proper shutdown
        logger.info("Shutting down")
        obs.shutdown() 