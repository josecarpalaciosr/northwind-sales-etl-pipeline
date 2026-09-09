"""Orchestrate the Northwind sales ETL pipeline."""

import logging
import sqlite3

from northwind_etl.extract import (
    SOURCE_DATABASE_PATH,
    extract_sales_order_lines,
)
from northwind_etl.load import (
    TARGET_DATABASE_PATH,
    load_sales_order_lines,
)
from northwind_etl.logging_config import configure_logging
from northwind_etl.transform import transform_sales_order_lines
from northwind_etl.validate import validate_sales_order_lines

logger = logging.getLogger(__name__)

def run_pipeline() -> None:
    """Extract and transform the Northwind sales data."""

    # Record the beginning of the complete ETL execution.
    logger.info("Pipeline started.")

    # Prevent SQLite from creating an empty database if the source is missing.
    if not SOURCE_DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Source database not found: {SOURCE_DATABASE_PATH}"
        )

    # Open the connection required by the extraction stage.
    connection = sqlite3.connect(SOURCE_DATABASE_PATH)

    try:
        # Extract sales lines from the source database into a DataFrame.
        extracted_data = extract_sales_order_lines(connection)

    finally:
        # The complete extraction is already in memory, so close the source.
        connection.close()

    # Record the dimensions only after extraction and connection closure succeed.
    logger.info(
        "Extraction completed: %s rows x %s columns.",
        f"{extracted_data.shape[0]:,}",
        extracted_data.shape[1],
    )

    # Clean and enrich the extracted DataFrame.
    transformed_data = transform_sales_order_lines(extracted_data)

    # Confirm that transformation preserved the line-level granularity.
    extracted_row_count = len(extracted_data)
    transformed_row_count = len(transformed_data)

    if transformed_row_count != extracted_row_count:
        raise ValueError(
            "Transformation changed the number of sales order lines."
        )

    # Record the dimensions after confirming line-level granularity.
    logger.info(
        "Transformation completed: %s rows x %s columns.",
        f"{transformed_data.shape[0]:,}",
        transformed_data.shape[1],
    )

    # Validate the transformed dataset before loading it.
    validate_sales_order_lines(transformed_data)

    # Record successful validation after every business rule has passed.
    logger.info(
        "Validation completed: %s sales order lines checked.",
        f"{len(transformed_data):,}",
    )

    # Load the validated DataFrame into the analytical SQLite database.
    loaded_row_count = load_sales_order_lines(transformed_data)

    # Record the confirmed number of rows persisted in the target table.
    logger.info(
        "Load completed: %s rows.",
        f"{loaded_row_count:,}",
    )

    # Record the location of the generated analytical database.
    logger.info("Target database: %s", TARGET_DATABASE_PATH)

    # Select representative analytical columns for optional debugging.
    preview_columns = [
        "OrderID",
        "ProductName",
        "OrderDate",
        "CustomerCountry",
        "EmployeeFullName",
        "GrossRevenue",
        "DiscountAmount",
        "NetRevenue",
    ]

    # Keep the preview available without displaying it during normal execution.
    logger.debug(
        "Transformed data preview:\n%s",
        transformed_data[preview_columns]
        .head(10)
        .to_string(index=False),
    )

    # Record successful completion only after every stage has finished.
    logger.info("Pipeline completed successfully.")

if __name__ == "__main__":
    # Configure logging only when this module starts the application.
    configure_logging()

    try:
        # Execute the complete ETL pipeline.
        run_pipeline()

    except Exception:
        # Record the error and its traceback before preserving the failure.
        logger.exception("Pipeline failed.")
        raise