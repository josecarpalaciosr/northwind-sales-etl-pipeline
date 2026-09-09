"""Tests for the Northwind sales data-validation stage."""

import pandas as pd
import pytest
from northwind_etl.validate import validate_sales_order_lines


def build_valid_sales_data() -> pd.DataFrame:
    """Create a minimal dataset that satisfies every validation rule."""

    return pd.DataFrame(
        {
            "OrderID": [10248, 10248],
            "ProductID": [11, 42],
            "Quantity": [12, 10],
            "UnitPrice": [14.00, 9.80],
            "Discount": [0.00, 0.10],
            "GrossRevenue": [168.00, 98.00],
            "DiscountAmount": [0.00, 9.80],
            "NetRevenue": [168.00, 88.20],
        }
    )


def test_validate_sales_order_lines_accepts_valid_data() -> None:
    """Verify that a structurally and financially valid dataset passes."""

    valid_data = build_valid_sales_data()

    validation_result = validate_sales_order_lines(valid_data)

    assert validation_result is None

def test_validate_sales_order_lines_rejects_duplicate_lines() -> None:
    """Verify that duplicated composite sales-line keys are rejected."""

    # Start with data that satisfies every validation rule.
    invalid_data = build_valid_sales_data()

    # Duplicate the first ProductID in the second row.
    # Both rows will now have the composite key (10248, 11).
    invalid_data.loc[1, "ProductID"] = 11

    # Validation must stop with the expected business-rule error.
    with pytest.raises(
        ValueError,
        match=r"^Found 1 duplicate sales order lines\.$",
    ):
        validate_sales_order_lines(invalid_data)

def test_validate_sales_order_lines_rejects_zero_quantity() -> None:
    """Verify that a sales line with zero quantity is rejected."""

    # Start with a dataset that satisfies every validation rule.
    invalid_data = build_valid_sales_data()

    # Set the first sales line to the invalid boundary value.
    invalid_data.loc[0, "Quantity"] = 0

    # Keep the financial values consistent with a zero-unit sale so that
    # quantity remains the only intentionally invalid business rule.
    invalid_data.loc[0, "GrossRevenue"] = 0.00
    invalid_data.loc[0, "DiscountAmount"] = 0.00
    invalid_data.loc[0, "NetRevenue"] = 0.00

    # Validation must reject the zero quantity with the expected error.
    with pytest.raises(
        ValueError,
        match=r"^Found 1 rows with invalid quantities\.$",
    ):
        validate_sales_order_lines(invalid_data)

def test_validate_sales_order_lines_rejects_negative_unit_price() -> None:
    """Verify that a sales line with a negative unit price is rejected."""

    # Start with a dataset that satisfies every validation rule.
    invalid_data = build_valid_sales_data()

    # Make the first historical unit price invalid.
    invalid_data.loc[0, "UnitPrice"] = -1.00

    # Keep the derived financial values consistent with the modified input
    # so that the negative price is the rule intentionally being tested.
    invalid_data.loc[0, "GrossRevenue"] = -12.00
    invalid_data.loc[0, "DiscountAmount"] = 0.00
    invalid_data.loc[0, "NetRevenue"] = -12.00

    # Validation must reject the negative historical unit price.
    with pytest.raises(
        ValueError,
        match=r"^Found 1 rows with negative unit prices\.$",
    ):
        validate_sales_order_lines(invalid_data)

def test_validate_sales_order_lines_rejects_discount_above_one() -> None:
    """Verify that a discount greater than 100 percent is rejected."""

    # Start with a dataset that satisfies every validation rule.
    invalid_data = build_valid_sales_data()

    # Set the first discount to 110 percent, above the accepted maximum.
    invalid_data.loc[0, "Discount"] = 1.10

    # Keep the derived financial values consistent with the modified
    # discount so that its invalid range is the targeted failure.
    invalid_data.loc[0, "DiscountAmount"] = 184.80
    invalid_data.loc[0, "NetRevenue"] = -16.80

    # Validation must reject a discount outside the inclusive 0-to-1 range.
    with pytest.raises(
        ValueError,
        match=r"^Found 1 rows with invalid discounts\.$",
    ):
        validate_sales_order_lines(invalid_data)

def test_validate_sales_order_lines_rejects_inconsistent_net_revenue() -> None:
    """Verify that an inconsistent net-revenue calculation is rejected."""

    # Start with a dataset that satisfies every validation rule.
    invalid_data = build_valid_sales_data()

    # Replace the correct first-row net revenue with an incorrect value.
    invalid_data.loc[0, "NetRevenue"] = 160.00

    # Validation must detect the inconsistency between the financial fields.
    with pytest.raises(
        ValueError,
        match=r"^Found 1 inconsistent values in NetRevenue\.$",
    ):
        validate_sales_order_lines(invalid_data)

def test_validate_sales_order_lines_rejects_empty_data() -> None:
    """Verify that an empty transformed dataset is rejected."""

    # Create a DataFrame with no rows and no columns.
    empty_data = pd.DataFrame()

    # Validation must stop before evaluating any other business rule.
    with pytest.raises(
        ValueError,
        match=r"^The transformed sales dataset is empty\.$",
    ):
        validate_sales_order_lines(empty_data)

def test_validate_sales_order_lines_rejects_missing_column() -> None:
    """Verify that a missing required column is reported."""

    # Start with a dataset that satisfies every validation rule.
    valid_data = build_valid_sales_data()

    # Create a new DataFrame without the required NetRevenue column.
    invalid_data = valid_data.drop(columns=["NetRevenue"])

    # Validation must identify the missing required column.
    with pytest.raises(
        ValueError,
        match=r"^Required columns are missing: \['NetRevenue'\]$",
    ):
        validate_sales_order_lines(invalid_data)

def test_validate_sales_order_lines_rejects_null_required_value() -> None:
    """Verify that a null value in a required column is rejected."""

    # Start with a dataset that satisfies every validation rule.
    invalid_data = build_valid_sales_data()

    # Remove the first historical unit price by assigning a null value.
    invalid_data.loc[0, "UnitPrice"] = pd.NA

    # Capture the expected validation error for later inspection.
    with pytest.raises(
        ValueError,
        match=(
            r"^Required columns contain null values: "
            r"\{'UnitPrice': 1\}$"
        ),
    ):
        validate_sales_order_lines(invalid_data)