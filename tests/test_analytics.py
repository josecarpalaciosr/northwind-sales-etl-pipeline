"""Integration tests for the analytical SQL queries."""

import sqlite3
from pathlib import Path

import pandas as pd
import pytest

from northwind_etl.extract import extract_sales_order_lines
from northwind_etl.load import load_sales_order_lines
from northwind_etl.transform import transform_sales_order_lines
from northwind_etl.validate import validate_sales_order_lines


# Resolve the project root from tests/test_analytics.py.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Define the directory containing the analytical SQL queries.
ANALYTICS_DIRECTORY = PROJECT_ROOT / "sql" / "analytics"

# Define the tracked Northwind source database used to build test data.
SOURCE_DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "northwind.db"
)

@pytest.fixture(scope="module")
def analytics_database_path(
    tmp_path_factory: pytest.TempPathFactory,
) -> Path:
    """Build a temporary analytical database for the SQL tests."""

    # Create a temporary directory managed automatically by pytest.
    # The module scope allows all analytical tests to reuse the same database.
    temporary_directory = tmp_path_factory.mktemp("analytics")

    # Define the temporary SQLite database without modifying the real
    # data/processed/northwind_analytics.db file.
    database_path = (
        temporary_directory
        / "northwind_analytics.db"
    )

    # Open the tracked Northwind source database and extract its sales data.
    with sqlite3.connect(SOURCE_DATABASE_PATH) as source_connection:
        extracted_data = extract_sales_order_lines(
            source_connection
        )

    # Apply the same cleaning, enrichment, and financial calculations
    # used by the production ETL pipeline.
    transformed_data = transform_sales_order_lines(
        extracted_data
    )

    # Confirm that the transformed dataset satisfies all structural,
    # business-rule, and financial validations before loading it.
    validate_sales_order_lines(transformed_data)

    # Load the validated data into the temporary analytical database.
    # This creates the sales_order_lines table and its indexes.
    load_sales_order_lines(
        transformed_data,
        database_path=database_path,
    )

    # Provide the temporary database path to every test that requests
    # the analytics_database_path fixture.
    return database_path

def execute_analytical_query(
    query_filename: str,
    database_path: Path,
) -> pd.DataFrame:
    """Execute an analytical SQL query against a database."""

    query_path = ANALYTICS_DIRECTORY / query_filename
    query = query_path.read_text(encoding="utf-8")

    with sqlite3.connect(database_path) as connection:
        return pd.read_sql_query(query, connection)

@pytest.mark.parametrize(
    ("query_filename", "expected_columns"),
    [
        (
            "monthly_sales_performance.sql",
            {
                "SalesMonth",
                "OrderCount",
                "UnitsSold",
                "GrossRevenue",
                "DiscountAmount",
                "NetRevenue",
                "PreviousMonthNetRevenue",
                "MonthOverMonthGrowthPercent",
            },
        ),
        (
            "product_performance.sql",
            {
                "CategoryID",
                "CategoryName",
                "ProductID",
                "ProductName",
                "NetRevenue",
                "CategoryRevenueSharePercent",
                "RevenueRankWithinCategory",
                "OverallRevenueRank",
            },
        ),
        (
            "country_performance.sql",
            {
                "CustomerCountry",
                "CustomerCount",
                "OrderCount",
                "SalesLineCount",
                "UnitsSold",
                "NetRevenue",
                "AverageOrderValue",
                "GlobalRevenueSharePercent",
                "RevenueRank",
            },
        ),
        (
            "employee_performance.sql",
            {
                "EmployeeID",
                "EmployeeFullName",
                "OrderCount",
                "UnitsSold",
                "NetRevenue",
                "AverageOrderValue",
                "OnTimeShipmentPercent",
                "RevenueRank",
            },
        ),
        (
            "discount_performance.sql",
            {
                "DiscountBand",
                "SalesLineCount",
                "OrderCount",
                "UnitsSold",
                "AverageDiscountPercent",
                "GrossRevenue",
                "DiscountAmount",
                "NetRevenue",
                "EffectiveDiscountRatePercent",
                "GlobalNetRevenueSharePercent",
            },
        ),
    ],
)

def test_analytical_query_executes_and_returns_expected_columns(
    query_filename: str,
    expected_columns: set[str],
    analytics_database_path: Path,
) -> None:
    """Confirm that each analytical query executes and returns its columns."""

    result = execute_analytical_query(
        query_filename,
        analytics_database_path,
    )

    assert not result.empty
    assert expected_columns.issubset(result.columns)

def test_monthly_sales_uses_previous_month_for_growth(
    analytics_database_path: Path,
) -> None:
    """Confirm that monthly growth compares consecutive months correctly."""

    result = execute_analytical_query(
        "monthly_sales_performance.sql",
        analytics_database_path,
    )

    sales_months = pd.to_datetime(result["SalesMonth"])

    # Confirm that the query returns the months chronologically.
    assert sales_months.is_monotonic_increasing

    # The first month cannot have a previous-month comparison.
    assert pd.isna(result.iloc[0]["PreviousMonthNetRevenue"])
    assert pd.isna(result.iloc[0]["MonthOverMonthGrowthPercent"])

    for position in range(1, len(result)):
        previous_net_revenue = result.iloc[position - 1]["NetRevenue"]
        current_net_revenue = result.iloc[position]["NetRevenue"]

        # LAG must retrieve the immediately preceding row's revenue.
        assert result.iloc[position][
            "PreviousMonthNetRevenue"
        ] == pytest.approx(
            previous_net_revenue,
            abs=0.01,
        )

        expected_growth = (
            (current_net_revenue - previous_net_revenue)
            / previous_net_revenue
            * 100
        )

        assert result.iloc[position][
            "MonthOverMonthGrowthPercent"
        ] == pytest.approx(
            expected_growth,
            abs=0.01,
        )

def test_product_performance_ranks_and_category_shares(
    analytics_database_path: Path,
) -> None:
    """Confirm product rankings and category revenue shares."""

    result = execute_analytical_query(
        "product_performance.sql",
        analytics_database_path,
    )

    # The product with the most revenue must occupy overall rank one.
    highest_revenue_product = result.loc[result["NetRevenue"].idxmax()]

    assert highest_revenue_product["OverallRevenueRank"] == 1

    # Every category must have at least one product ranked first.
    for _, category_products in result.groupby("CategoryID"):
        assert category_products["RevenueRankWithinCategory"].min() == 1

        assert category_products[
            "CategoryRevenueSharePercent"
        ].sum() == pytest.approx(
            100,
            abs=0.10,
        )

def test_country_performance_global_shares_and_ranking(
    analytics_database_path: Path,
) -> None:
    """Confirm country revenue shares and ranking."""

    result = execute_analytical_query(
        "country_performance.sql",
        analytics_database_path,
    )

    highest_revenue_country = result.loc[result["NetRevenue"].idxmax()]

    assert highest_revenue_country["RevenueRank"] == 1

    assert result["GlobalRevenueSharePercent"].sum() == pytest.approx(
        100,
        abs=0.10,
    )

    assert result["AverageOrderValue"].gt(0).all()

def test_employee_performance_metrics_are_valid(
    analytics_database_path: Path,
) -> None:
    """Confirm employee performance percentages and ranking."""

    result = execute_analytical_query(
        "employee_performance.sql",
        analytics_database_path,
    )

    highest_revenue_employee = result.loc[result["NetRevenue"].idxmax()]

    assert highest_revenue_employee["RevenueRank"] == 1

    assert result["OrderCount"].gt(0).all()
    assert result["AverageOrderValue"].gt(0).all()

    on_time_percentages = result["OnTimeShipmentPercent"].dropna()

    assert on_time_percentages.between(0, 100).all()

def test_discount_performance_global_shares_and_rates(
    analytics_database_path: Path,
) -> None:
    """Confirm discount-band shares and effective rates."""

    result = execute_analytical_query(
        "discount_performance.sql",
        analytics_database_path,
    )

    assert result["GlobalNetRevenueSharePercent"].sum() == pytest.approx(
        100,
        abs=0.10,
    )

    assert result["AverageDiscountPercent"].between(0, 100).all()
    assert result["EffectiveDiscountRatePercent"].between(0, 100).all()

    no_discount = result.loc[
        result["DiscountBand"] == "No discount"
    ].iloc[0]

    assert no_discount["AverageDiscountPercent"] == pytest.approx(0)
    assert no_discount["EffectiveDiscountRatePercent"] == pytest.approx(0)
    assert no_discount["DiscountAmount"] == pytest.approx(0)