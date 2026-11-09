"""Tests for the central analytical dataset export."""

import sqlite3
from pathlib import Path

import pandas as pd
import pytest

from northwind_etl.export_analytics import (
    FACT_EXPORT_FILENAME,
    export_fact_dataset,
)


def test_export_fact_dataset_creates_csv_file(
    tmp_path: Path,
) -> None:
    """Confirm that the central fact dataset is exported correctly."""

    # Define a temporary analytical database used only by this test.
    database_path = tmp_path / "analytics.db"

    # Create a small representative sales fact table.
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE sales_order_lines (
                OrderID INTEGER NOT NULL,
                ProductID INTEGER NOT NULL,
                OrderDate TEXT NOT NULL,
                Quantity INTEGER NOT NULL,
                NetRevenue REAL NOT NULL
            )
            """
        )

        connection.executemany(
            """
            INSERT INTO sales_order_lines (
                OrderID,
                ProductID,
                OrderDate,
                Quantity,
                NetRevenue
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (10249, 51, "2012-07-05", 40, 1696.00),
                (10248, 42, "2012-07-04", 10, 98.00),
            ],
        )

        connection.commit()

    output_directory = tmp_path / "exports"

    # Execute the export using temporary test paths.
    exported_row_count = export_fact_dataset(
        database_path=database_path,
        output_directory=output_directory,
    )

    export_path = output_directory / FACT_EXPORT_FILENAME

    # Confirm that the CSV was created and contains both source rows.
    assert export_path.exists()
    assert exported_row_count == 2

    exported_data = pd.read_csv(export_path)

    # Confirm that all source columns were preserved without an index.
    assert list(exported_data.columns) == [
        "OrderID",
        "ProductID",
        "OrderDate",
        "Quantity",
        "NetRevenue",
    ]

    # Confirm that the deterministic ordering was applied.
    assert exported_data["OrderID"].tolist() == [
        10248,
        10249,
    ]

    assert exported_data["ProductID"].tolist() == [
        42,
        51,
    ]

    assert exported_data["NetRevenue"].tolist() == pytest.approx(
        [
            98.00,
            1696.00,
        ]
    )


def test_export_fact_dataset_rejects_missing_database(
    tmp_path: Path,
) -> None:
    """Confirm that exporting fails clearly when the database is missing."""

    missing_database_path = tmp_path / "missing.db"
    output_directory = tmp_path / "exports"

    with pytest.raises(
        FileNotFoundError,
        match="Analytical database not found",
    ):
        export_fact_dataset(
            database_path=missing_database_path,
            output_directory=output_directory,
        )

    # Confirm that SQLite did not silently create an empty database.
    assert not missing_database_path.exists()


def test_export_fact_dataset_rejects_missing_fact_table(
    tmp_path: Path,
) -> None:
    """Confirm that exporting fails when the fact table is missing."""

    database_path = tmp_path / "analytics.db"

    # Create an existing SQLite database without the required fact table.
    with sqlite3.connect(database_path):
        pass

    output_directory = tmp_path / "exports"

    with pytest.raises(
        ValueError,
        match="Required analytical table not found",
    ):
        export_fact_dataset(
            database_path=database_path,
            output_directory=output_directory,
        )