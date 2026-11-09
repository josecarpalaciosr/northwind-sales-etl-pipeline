"""Export the central validated sales fact dataset consumed by Power BI."""

import sqlite3
from pathlib import Path

import pandas as pd

from northwind_etl.load import TARGET_DATABASE_PATH


# Resolve the project root from src/northwind_etl/export_analytics.py.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Define the directory receiving the generated reporting dataset.
EXPORT_DIRECTORY = PROJECT_ROOT / "data" / "exports"

# Define the validated analytical table used as the Power BI fact table.
FACT_TABLE_NAME = "sales_order_lines"

# Define the central dataset generated for Power BI.
FACT_EXPORT_FILENAME = "sales_order_line_fact.csv"

# Export the fact table in a deterministic order.
FACT_EXPORT_QUERY = """
SELECT *
FROM sales_order_lines
ORDER BY OrderID, ProductID
"""


def export_fact_dataset(
    database_path: Path = TARGET_DATABASE_PATH,
    output_directory: Path = EXPORT_DIRECTORY,
) -> int:
    """Export the validated sales fact table to a CSV dataset."""

    # Prevent SQLite from silently creating an empty database when the
    # expected analytical database does not exist.
    if not database_path.exists():
        raise FileNotFoundError(
            f"Analytical database not found: {database_path}"
        )

    # Create the export directory when it does not already exist.
    output_directory.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(database_path) as connection:
        # Confirm that the required analytical fact table exists.
        table_exists = connection.execute(
            """
            SELECT 1
            FROM sqlite_master
            WHERE type = 'table'
              AND name = ?
            """,
            (FACT_TABLE_NAME,),
        ).fetchone()

        if table_exists is None:
            raise ValueError(
                f"Required analytical table not found: {FACT_TABLE_NAME}"
            )

        # Read the complete validated sales fact table.
        fact_data = pd.read_sql_query(
            FACT_EXPORT_QUERY,
            connection,
        )

    # Export the dataset without adding a DataFrame index.
    export_path = output_directory / FACT_EXPORT_FILENAME
    fact_data.to_csv(
        export_path,
        index=False,
        encoding="utf-8",
    )

    return len(fact_data)


def main() -> None:
    """Export the central Power BI dataset and report its row count."""

    row_count = export_fact_dataset()

    print(
        f"Exported {FACT_EXPORT_FILENAME}: "
        f"{row_count:,} rows"
    )


if __name__ == "__main__":
    main()