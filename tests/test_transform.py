"""Tests for the Northwind sales data-transformation stage."""

import pandas as pd
import pytest

from northwind_etl.transform import transform_sales_order_lines

EXPECTED_DATE_COLUMNS = (
    "OrderDate",
    "RequiredDate",
    "ShippedDate",
)

def build_extracted_sales_data() -> pd.DataFrame:
    """Create a minimal representative extracted sales dataset."""

    return pd.DataFrame(
        {
            "OrderID": [10248, 10249],
            "ProductID": [11, 14],
            "OrderDate": [
                "2016-07-04",
                "2016-07-05 09:23:46",
            ],
            "RequiredDate": [
                "2016-08-01",
                "2016-08-02",
            ],
            "ShippedDate": [
                "2016-07-16",
                None,
            ],
            "CustomerCountry": [
                None,
                "Germany",
            ],
            "EmployeeFirstName": [
                " Steven ",
                "Michael",
            ],
            "EmployeeLastName": [
                "Buchanan ",
                " Suyama ",
            ],
            "UnitPrice": [14.00, 9.80],
            "Quantity": [12, 10],
            "Discount": [0.00, 0.10],
        }
    )


def test_transform_sales_order_lines_converts_iso_dates() -> None:
    """Verify that ISO date strings become Pandas datetime columns."""

    extracted_data = build_extracted_sales_data()

    transformed_data = transform_sales_order_lines(extracted_data)

    for column_name in EXPECTED_DATE_COLUMNS:
        assert pd.api.types.is_datetime64_any_dtype(
            transformed_data[column_name]
        )

    assert transformed_data.loc[0, "OrderDate"] == pd.Timestamp(
        "2016-07-04"
    )
    assert transformed_data.loc[1, "OrderDate"] == pd.Timestamp(
        "2016-07-05 09:23:46"
    )
    assert pd.isna(transformed_data.loc[1, "ShippedDate"])

def test_transform_sales_order_lines_fills_missing_customer_country() -> None:
    """Verify that missing customer countries receive an analytical label."""

    # Create representative extracted data containing one missing country.
    extracted_data = build_extracted_sales_data()

    # Apply the complete sales transformation.
    transformed_data = transform_sales_order_lines(extracted_data)

    # The missing country must be replaced with the explicit analytical label.
    assert transformed_data.loc[0, "CustomerCountry"] == "Unknown"

    # An existing country must remain unchanged.
    assert transformed_data.loc[1, "CustomerCountry"] == "Germany"

def test_transform_sales_order_lines_builds_clean_employee_names() -> None:
    """Verify that employee names are trimmed and combined correctly."""

    # Create extracted data containing employee names with extra spaces.
    extracted_data = build_extracted_sales_data()

    # Apply the sales transformation.
    transformed_data = transform_sales_order_lines(extracted_data)

    # Surrounding spaces must be removed before combining the first employee.
    assert transformed_data.loc[0, "EmployeeFullName"] == "Steven Buchanan"

    # The same cleaning and combination must apply to the second employee.
    assert transformed_data.loc[1, "EmployeeFullName"] == "Michael Suyama"

def test_transform_sales_order_lines_calculates_financial_metrics() -> None:
    """Verify gross, discount and net revenue calculations."""

    # Create extracted data with different prices, quantities and discounts.
    extracted_data = build_extracted_sales_data()

    # Apply the transformation that creates the financial columns.
    transformed_data = transform_sales_order_lines(extracted_data)

    # Gross revenue equals the historical unit price multiplied by quantity.
    assert transformed_data["GrossRevenue"].tolist() == pytest.approx(
        [168.00, 98.00]
    )

    # Discount amount equals gross revenue multiplied by the discount rate.
    assert transformed_data["DiscountAmount"].tolist() == pytest.approx(
        [0.00, 9.80]
    )

    # Net revenue equals gross revenue minus the discount amount.
    assert transformed_data["NetRevenue"].tolist() == pytest.approx(
        [168.00, 88.20]
    )

def test_transform_sales_order_lines_preserves_original_data() -> None:
    """Verify that transformation does not modify the extracted DataFrame."""

    # Create the extracted data supplied to the transformation.
    extracted_data = build_extracted_sales_data()

    # Preserve an independent snapshot of its original contents.
    original_data = extracted_data.copy()

    # Transform the data and retain the returned DataFrame.
    transformed_data = transform_sales_order_lines(extracted_data)

    # The DataFrame supplied as input must retain its original contents.
    pd.testing.assert_frame_equal(extracted_data, original_data)

    # The transformation must return a different DataFrame object.
    assert transformed_data is not extracted_data