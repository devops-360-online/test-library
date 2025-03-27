#!/usr/bin/env python3
"""
Example demonstrating standardized observability formats.

This script shows how the library automatically applies standard naming,
attributes, and formats to all observability signals.
"""

import time
import random
import pandas as pd
import numpy as np
from datetime import datetime

from simple_observability import ObservabilityClient
from simple_observability.standards import AttributeNames, Environment

# Initialize with standardized environment
obs = ObservabilityClient(
    service_name="standardized-example",
    environment=Environment.DEVELOPMENT.value,  # Uses standard enum values
    # We'll use structured log format but not JSON for better demo readability
    json_logs=False
)

# Get a data-aware logger
logger = obs.get_logger()

# Demonstrate standardized metrics
def create_standardized_metrics():
    """Create metrics with standardized names and attributes."""
    logger.info("Creating standardized metrics")
    
    # These metric names will be automatically standardized to snake_case
    # with consistent naming patterns
    metrics = {
        # Counter for rows (automatically gets unit="rows" and standard attributes)
        "rowsProcessed": obs.create_counter(
            name="data_processed_rows_total",  # Standard prefix and suffix
            description="Total number of data rows processed",
            unit="rows",
            attributes={
                "data_type": "customer",
                AttributeNames.DATA_SOURCE: "database"  # Using standard attribute name
            }
        ),
        
        # Histogram for processing time (automatically gets unit="s" and standard attributes)
        "processingTime": obs.create_histogram(
            name="data_processing_duration_seconds", 
            description="Time taken to process data",
            unit="s",
            attributes={
                AttributeNames.DATA_OPERATION: "transform"  # Using standard attribute name
            }
        ),
        
        # Gauge for memory usage
        "memoryUsage": obs.create_gauge(
            name="memory_usage_bytes",
            description="Memory usage during processing",
            unit="By"
        )
    }
    
    return metrics

# Demonstrate standardized data operations with spans
@obs.trace_data_processing(attributes={
    AttributeNames.DATA_SOURCE: "synthetic",
    "record_type": "customer"
})
def generate_test_data(rows=1000):
    """Generate test data with trace information automatically added."""
    # The decorator automatically:
    # 1. Maps this function to a standard operation name
    # 2. Adds standard attributes
    # 3. Includes DataFrame shape information
    
    logger.info(f"Generating {rows} rows of test data")
    
    # Create sample data
    data = {
        'customer_id': [f'CUST-{i:05d}' for i in range(rows)],
        'value': np.random.uniform(100, 10000, rows),
        'category': np.random.choice(['A', 'B', 'C'], size=rows),
        'timestamp': [datetime.now().isoformat() for _ in range(rows)]
    }
    
    # Add some missing values
    for col in data:
        if col != 'customer_id':
            missing_indices = np.random.choice(
                range(rows), size=int(rows * 0.05), replace=False
            )
            for idx in missing_indices:
                data[col][idx] = None
    
    df = pd.DataFrame(data)
    logger.info(f"Generated DataFrame with shape {df.shape}")
    return df

def process_data(metrics):
    """Process data with standardized logs and spans."""
    # Use the high-level data operation context manager with standard naming
    with obs.data_operation(
        operation_type="load",  # Will be mapped to standard operation name
        target="customer_data",  # The data source
        attributes={"format": "csv"}
    ) as span:
        # This creates a span with name "data.load.customer_data" and standard attributes
        start_time = time.time()
        df = generate_test_data()
        metrics["rowsProcessed"].add(len(df))
        duration = time.time() - start_time
        metrics["processingTime"].record(duration)
        
        # Show how to add structured data to logs
        with logger.with_data(
            data_size=len(df),
            operation="data_generation",
            duration_ms=duration * 1000
        ):
            logger.info("Data generation complete")
    
    # Another standardized data operation
    with obs.data_operation("clean", "customer_data") as span:
        start_time = time.time()
        
        # Simple cleaning operation
        original_size = len(df)
        df_clean = df.dropna()
        rows_removed = original_size - len(df_clean)
        
        # Record standard metrics
        duration = time.time() - start_time
        metrics["processingTime"].record(duration, {"stage": "cleaning"})
        
        # Add span attributes in standard format
        span.set_attribute(AttributeNames.DATA_ROWS, len(df_clean))
        span.set_attribute("rows_removed", rows_removed)
        
        # Add structured context to log messages
        logger.data(
            level=logging.INFO,
            msg=f"Cleaned data by removing {rows_removed} rows with missing values",
            data={
                "original_size": original_size,
                "cleaned_size": len(df_clean),
                "duration_ms": duration * 1000
            }
        )
    
    # Final operation
    with obs.data_operation("transform", "customer_data") as span:
        start_time = time.time()
        
        # Simple transformation - add a new column
        df_clean['value_category'] = df_clean.apply(
            lambda row: 'high' if row['value'] > 5000 else 'low', 
            axis=1
        )
        
        # Update metrics
        duration = time.time() - start_time
        metrics["processingTime"].record(duration, {"stage": "transform"})
        
        # Log with context
        logger.info(f"Added value_category column in {duration:.3f}s")
    
    return df_clean

def main():
    """Run the standardized example."""
    logger.info("Starting standardized observability example")
    
    # Create standardized metrics
    metrics = create_standardized_metrics()
    
    # Use the high-level timed_task context manager
    # This creates standard success/failure/duration metrics
    with obs.timed_task("data_workflow", {"example": "standardized"}) as ctx:
        # Simulate memory usage
        current_memory = random.randint(100_000_000, 200_000_000)  # 100-200 MB
        metrics["memoryUsage"].add(current_memory)
        
        # Process the data with standardized observability
        result_df = process_data(metrics)
        
        # Update memory after processing
        current_memory = random.randint(200_000_000, 300_000_000)  # 200-300 MB
        metrics["memoryUsage"].add(current_memory)
        
        logger.info(f"Processed data successfully, final shape: {result_df.shape}")
        
        # Show final statistics with structured logging
        high_value_count = (result_df['value_category'] == 'high').sum()
        low_value_count = (result_df['value_category'] == 'low').sum()
        
        logger.data(
            level=logging.INFO,
            msg="Processing summary statistics",
            data={
                "total_records": len(result_df),
                "high_value_count": high_value_count,
                "low_value_count": low_value_count,
                "memory_bytes": current_memory
            }
        )

if __name__ == "__main__":
    import logging  # Import here to avoid issues with custom logging setup
    
    try:
        main()
    except Exception as e:
        logger.exception(f"Error in standardized example: {e}")
    finally:
        # Explicitly shutdown to flush telemetry
        obs.shutdown() 