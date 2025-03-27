#!/usr/bin/env python3
"""
Real-world example of using the simple_observability library.

This script demonstrates how a data engineer or data scientist
would use the library in their data processing pipeline.
"""

import logging
import time
import random
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# Import the observability client
from simple_observability import ObservabilityClient

# Initialize observability with just a service name
# Everything else has sensible defaults
obs = ObservabilityClient(service_name="data-processor")

# Get a logger that's automatically configured with structured logging
logger = obs.get_logger()


# Use the decorator to automatically trace and time this function
@obs.trace_data_processing(attributes={"data_source": "customer_data"})
def load_data(filename: str) -> pd.DataFrame:
    """Load data from a CSV file."""
    logger.info(f"Loading data from {filename}")
    
    # In a real scenario, you'd load from a file
    # Here we'll simulate it for the example
    if not filename.endswith('.csv'):
        raise ValueError(f"Unsupported file format: {filename}")
    
    # Simulate loading time
    time.sleep(random.uniform(0.5, 1.0))
    
    # Generate some sample data
    columns = ['customer_id', 'value', 'timestamp']
    data = []
    for i in range(1000):
        data.append([
            f"CUST-{i:05d}",
            random.uniform(100, 10000),
            datetime.now().isoformat()
        ])
    
    df = pd.DataFrame(data, columns=columns)
    logger.info(f"Loaded {len(df)} rows with columns: {', '.join(df.columns)}")
    
    return df


@obs.trace_data_processing(attributes={"transformation": "clean"})
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and prepare the data."""
    logger.info(f"Cleaning data with shape {df.shape}")
    
    # Create a copy to avoid modifying the original
    result = df.copy()
    
    # Convert customer_id to string if it's not already
    result['customer_id'] = result['customer_id'].astype(str)
    
    # Simulate some cleaning operations
    # 1. Remove any rows with missing values
    initial_rows = len(result)
    result = result.dropna()
    removed_rows = initial_rows - len(result)
    
    # 2. Filter out rows with negative values
    negative_mask = result['value'] <= 0
    negative_count = negative_mask.sum()
    result = result[~negative_mask]
    
    # Log what happened
    logger.info(f"Removed {removed_rows} rows with missing values")
    logger.info(f"Removed {negative_count} rows with negative or zero values")
    logger.info(f"Final clean data shape: {result.shape}")
    
    return result


@obs.trace_data_processing(attributes={"transformation": "aggregate"})
def aggregate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate the data by customer."""
    logger.info(f"Aggregating data with shape {df.shape}")
    
    # Simulate processing time
    time.sleep(random.uniform(0.3, 0.7))
    
    # Group by customer_id and calculate some metrics
    result = df.groupby('customer_id').agg({
        'value': ['sum', 'mean', 'count']
    }).reset_index()
    
    # Flatten the multi-level columns
    result.columns = ['customer_id', 'total_value', 'average_value', 'transaction_count']
    
    logger.info(f"Aggregated to {len(result)} customer records")
    
    return result


def process_file(filename: str) -> pd.DataFrame:
    """Process a single file with full metrics and tracing."""
    # Create specific metrics for this process
    metrics = {
        "processing_time": obs.create_histogram(
            name="file_processing_seconds",
            description="Time to process a file",
            unit="s"
        ),
        "row_count": obs.create_counter(
            name="processed_rows_total",
            description="Number of rows processed",
            unit="rows"
        ),
        "customer_count": obs.create_counter(
            name="processed_customers_total",
            description="Number of unique customers processed",
            unit="customers"
        )
    }
    
    # Track the entire process as a timed task with auto-metrics
    with obs.timed_task("file_processing", {"filename": filename}) as ctx:
        start_time = time.time()
        
        try:
            # Load the data 
            df = load_data(filename)
            metrics["row_count"].add(len(df), {"stage": "loaded"})
            
            # Clean the data
            df_clean = clean_data(df)
            metrics["row_count"].add(len(df_clean), {"stage": "cleaned"})
            
            # Aggregate the data
            df_agg = aggregate_data(df_clean)
            
            # Record customer count
            customer_count = len(df_agg)
            metrics["customer_count"].add(customer_count)
            
            # Calculate and record processing time
            processing_time = time.time() - start_time
            metrics["processing_time"].record(processing_time)
            
            logger.info(f"File processing complete in {processing_time:.2f} seconds")
            logger.info(f"Processed {len(df)} rows into {customer_count} customer records")
            
            return df_agg
            
        except Exception as e:
            logger.error(f"Error processing file {filename}: {str(e)}")
            # The trace_function decorator will automatically mark the span as failed
            # and record the exception
            raise


def main():
    """Main function to demonstrate the workflow."""
    logger.info("Data processing pipeline starting")
    
    try:
        # In a real application, you might get filenames from arguments
        filenames = ["customers_2023-01.csv", "customers_2023-02.csv"]
        
        results = []
        for filename in filenames:
            logger.info(f"Processing file: {filename}")
            result = process_file(filename)
            results.append(result)
        
        # Combine all results
        if results:
            combined = pd.concat(results)
            logger.info(f"Combined {len(combined)} customer records from {len(results)} files")
        
        logger.info("Data processing pipeline completed successfully")
        
    except Exception as e:
        logger.exception("Pipeline failed with error")
        sys.exit(1)


if __name__ == "__main__":
    # Run the pipeline
    main()
    
    # Clean shutdown
    # Note: this is optional as ObservabilityClient registers an atexit handler by default
    obs.shutdown() 