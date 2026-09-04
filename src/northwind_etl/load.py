"""Load transformed Northwind sales data into an analytical database."""

import sqlite3
from pathlib import Path

import pandas as pd


# Resolve the project root from src/northwind_etl/load.py.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Define the generated analytical SQLite database.
TARGET_DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "northwind_analytics.db"
)

# Define the analytical table receiving the transformed sales data.
TARGET_TABLE_NAME = "sales_order_lines"


def load_sales_order_lines(
    data: pd.DataFrame,
    database_path: Path = TARGET_DATABASE_PATH,
) -> int:
    """Load validated sales order lines into an analytical SQLite database."""

    # Ensure that the destination directory exists.
    database_path.parent.mkdir(parents=True, exist_ok=True)

    # Open a connection to the analytical SQLite database.
    connection = sqlite3.connect(database_path)

    try:
        # Perform a full-refresh load.
        # Re-running the pipeline replaces the table instead of duplicating rows.
        data.to_sql(
            name=TARGET_TABLE_NAME,
            con=connection,
            if_exists="replace",
            index=False,
            chunksize=10_000,
        )

        # Create a unique index using the original sales-line composite key.
        connection.execute(
            """
            CREATE UNIQUE INDEX idx_sales_order_lines_key
            ON sales_order_lines (OrderID, ProductID)
            """
        )

        # Improve queries that filter or group sales by order date.
        connection.execute(
            """
            CREATE INDEX idx_sales_order_lines_order_date
            ON sales_order_lines (OrderDate)
            """
        )

        # Improve queries that analyze sales by customer country.
        connection.execute(
            """
            CREATE INDEX idx_sales_order_lines_customer_country
            ON sales_order_lines (CustomerCountry)
            """
        )

        # Count the rows stored in the analytical table.
        loaded_row_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM sales_order_lines
            """
        ).fetchone()[0]

        # Compare the loaded rows with the validated DataFrame.
        if loaded_row_count != len(data):
            raise ValueError(
                "Loaded row count does not match the transformed dataset."
            )

        # Permanently save the table and its indexes.
        connection.commit()

    except Exception:
        # Undo pending database operations when an error occurs.
        connection.rollback()
        raise

    finally:
        # Always release the database connection.
        connection.close()

    # Return the count so pipeline.py can report the load result.
    return loaded_row_count