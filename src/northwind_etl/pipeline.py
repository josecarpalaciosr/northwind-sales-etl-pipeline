"""Orchestrate the Northwind sales ETL pipeline."""

import sqlite3

from northwind_etl.extract import (
    SOURCE_DATABASE_PATH,
    extract_sales_order_lines,
)
from northwind_etl.transform import transform_sales_order_lines


def run_pipeline() -> None:
    """Extract and transform the Northwind sales data."""

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

    # Clean and enrich the extracted DataFrame.
    transformed_data = transform_sales_order_lines(extracted_data)

    # Confirm that transformation preserved the line-level granularity.
    extracted_row_count = len(extracted_data)
    transformed_row_count = len(transformed_data)

    if transformed_row_count != extracted_row_count:
        raise ValueError(
            "Transformation changed the number of sales order lines."
        )

    # Display the dimensions produced by each pipeline stage.
    print(
        f"Extracted shape: "
        f"{extracted_data.shape[0]:,} rows x "
        f"{extracted_data.shape[1]} columns"
    )
    print(
        f"Transformed shape: "
        f"{transformed_data.shape[0]:,} rows x "
        f"{transformed_data.shape[1]} columns"
    )

    # Display selected transformed columns for manual verification.
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

    print("\nTransformed data preview:")
    print(
        transformed_data[preview_columns]
        .head(10)
        .to_string(index=False)
    )

if __name__ == "__main__":
    run_pipeline()