"""Extract sales data from the Northwind source database."""

from pathlib import Path
import sqlite3
import pandas as pd


# Locate the project root independently of where the repository is cloned.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Define the source database and SQL query locations.
SOURCE_DATABASE_PATH = PROJECT_ROOT / "data" / "raw" / "northwind.db"
SALES_QUERY_PATH = (
    PROJECT_ROOT / "sql" / "extraction" / "sales_order_lines.sql"
)


def extract_sales_order_lines(
    connection: sqlite3.Connection,
) -> pd.DataFrame:
    """Execute the sales extraction query and return its results."""

    # Read the SQL statement from its separate .sql file.
    query = SALES_QUERY_PATH.read_text(encoding="utf-8")

    # Execute the query and load its result into a Pandas DataFrame.
    return pd.read_sql_query(query, connection)


def main() -> None:
    """Run a sample sales extraction and display its result."""

    # Stop with a clear error if the source database is unavailable.
    if not SOURCE_DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Source database not found: {SOURCE_DATABASE_PATH}"
        )

    # Stop if the extraction query was not created or was misplaced.
    if not SALES_QUERY_PATH.exists():
        raise FileNotFoundError(
            f"Sales query not found: {SALES_QUERY_PATH}"
        )

    # Open a connection to the source SQLite database.
    connection = sqlite3.connect(SOURCE_DATABASE_PATH)

    try:
         # Execute the SQL query and receive its result as a DataFrame.
        sales_order_lines = extract_sales_order_lines(connection)

        # Display only a preview while retaining the complete extracted dataset.
        print(sales_order_lines.head(10).to_string(index=False))

        # Separate the DataFrame dimensions into rows and columns.
        row_count, column_count = sales_order_lines.shape

        # Display a summary of the extracted dataset dimensions.
        print(f"\nExtracted shape: {row_count} rows x {column_count} columns")

    finally:
        # Always close the connection, even if an error occurs.
        connection.close()


if __name__ == "__main__":
    main()