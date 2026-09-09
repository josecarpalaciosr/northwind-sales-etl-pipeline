"""Tests for the Northwind analytical data-loading stage."""

import sqlite3
import pandas as pd

from northwind_etl.load import (
    TARGET_TABLE_NAME,
    load_sales_order_lines,
)


def test_load_sales_order_lines_creates_table_and_indexes(tmp_path) -> None:
    """Verify that loading creates the table, rows, and expected indexes."""

    # Create a small representative dataset instead of using the full source.
    test_data = pd.DataFrame(
        {
            "OrderID": [10248, 10248, 10249],
            "ProductID": [11, 42, 14],
            "OrderDate": [
                "2016-07-04",
                "2016-07-04",
                "2016-07-05",
            ],
            "CustomerCountry": [
                "France",
                "France",
                "Germany",
            ],
        }
    )

    # Store the test database in a temporary directory managed by pytest.
    test_database_path = tmp_path / "test_analytics.db"

    # Execute the real loading function using the temporary database.
    loaded_row_count = load_sales_order_lines(
        test_data,
        test_database_path,
    )

    # Open the generated test database to inspect its persisted contents.
    connection = sqlite3.connect(test_database_path)

    try:
        stored_row_count = connection.execute(
            f"SELECT COUNT(*) FROM {TARGET_TABLE_NAME}"
        ).fetchone()[0]

        index_rows = connection.execute(
            f"PRAGMA index_list({TARGET_TABLE_NAME})"
        ).fetchall()

        index_names = set()

        for row in index_rows:
            index_names.add(row[1])

    finally:
        connection.close()

    # Compare the actual results against the expected results.
    assert loaded_row_count == len(test_data)
    assert stored_row_count == len(test_data)
    assert index_names == {
        "idx_sales_order_lines_key",
        "idx_sales_order_lines_order_date",
        "idx_sales_order_lines_customer_country",
    }

def test_load_sales_order_lines_replaces_existing_data(tmp_path) -> None:
    """Verify that a full refresh replaces previously loaded records."""

    # Represent the dataset already stored by an earlier pipeline execution.
    initial_data = pd.DataFrame(
        {
            "OrderID": [10248, 10249],
            "ProductID": [11, 14],
            "OrderDate": [
                "2016-07-04",
                "2016-07-05",
            ],
            "CustomerCountry": [
                "France",
                "Germany",
            ],
        }
    )

    # Represent a later full dataset with different records.
    # Using different values makes unintended data accumulation detectable.
    replacement_data = pd.DataFrame(
        {
            "OrderID": [10250],
            "ProductID": [51],
            "OrderDate": ["2016-07-08"],
            "CustomerCountry": ["Brazil"],
        }
    )

    # Use a temporary database so the production analytical database is
    # never created, replaced, or modified during the test.
    test_database_path = tmp_path / "test_analytics.db"

    # Establish the initial state of the temporary analytical database.
    initial_loaded_row_count = load_sales_order_lines(
        initial_data,
        test_database_path,
    )

    # Run a second full refresh against the same temporary database.
    replacement_loaded_row_count = load_sales_order_lines(
        replacement_data,
        test_database_path,
    )

    # Inspect the persisted result independently from the loading function.
    connection = sqlite3.connect(test_database_path)

    try:
        stored_row_count = connection.execute(
            f"SELECT COUNT(*) FROM {TARGET_TABLE_NAME}"
        ).fetchone()[0]

        stored_order_ids = connection.execute(
            f"SELECT OrderID FROM {TARGET_TABLE_NAME}"
        ).fetchall()

    finally:
        # Always release the temporary SQLite database connection.
        connection.close()

    # Confirm that both executions reported their expected row counts.
    assert initial_loaded_row_count == len(initial_data)
    assert replacement_loaded_row_count == len(replacement_data)

    # Confirm that only the replacement dataset remains in SQLite.
    assert stored_row_count == len(replacement_data)
    assert stored_order_ids == [(10250,)]