"""Validate transformed Northwind sales data."""

import pandas as pd

# Columns required to validate the structure and financial calculations.
REQUIRED_COLUMNS = {
    "OrderID",
    "ProductID",
    "Quantity",
    "UnitPrice",
    "Discount",
    "GrossRevenue",
    "DiscountAmount",
    "NetRevenue",
}

def validate_sales_order_lines(data: pd.DataFrame) -> None:
    """Validate transformed sales data using structural and business rules."""

    # Stop the pipeline if the transformation produced no sales records.
    if data.empty:
        raise ValueError("The transformed sales dataset is empty.")

    # Compare the required columns with the actual DataFrame columns.
    missing_columns = REQUIRED_COLUMNS.difference(data.columns)

    # Stop the pipeline if one or more required columns are missing.
    if missing_columns:
        raise ValueError(
            f"Required columns are missing: {sorted(missing_columns)}"
        )

    # Count null values in each required column.
    null_counts = data[list(REQUIRED_COLUMNS)].isna().sum()

    # Keep only the columns containing at least one null value.
    columns_with_nulls = null_counts[null_counts > 0]

    # Stop the pipeline if required data is incomplete.
    if not columns_with_nulls.empty:
        raise ValueError(
            "Required columns contain null values: "
            f"{columns_with_nulls.to_dict()}"
        )

    # Count duplicated sales lines using the original composite key.
    # In Order Details, OrderID and ProductID identify one sales line.
    duplicate_line_count = data.duplicated(
        subset=["OrderID", "ProductID"]
    ).sum()

    # Stop the pipeline if the same sales line appears more than once.
    if duplicate_line_count > 0:
        raise ValueError(
            f"Found {duplicate_line_count:,} duplicate sales order lines."
        )

    # Count sales lines with zero or negative quantities.
    invalid_quantity_count = (data["Quantity"] <= 0).sum()

    # A valid Northwind sales line should contain at least one unit.
    if invalid_quantity_count > 0:
        raise ValueError(
            f"Found {invalid_quantity_count:,} rows with invalid quantities."
        )

    # Count sales lines containing negative historical unit prices.
    invalid_price_count = (data["UnitPrice"] < 0).sum()

    # Historical sales prices may be zero, but cannot be negative.
    if invalid_price_count > 0:
        raise ValueError(
            f"Found {invalid_price_count:,} rows with negative unit prices."
        )

    # between(0, 1) returns True for valid discount proportions.
    # The ~ operator reverses the result to identify invalid discounts.
    invalid_discount_count = (
        ~data["Discount"].between(0, 1)
    ).sum()

    # Stop the pipeline if a discount is below 0 or above 1.
    if invalid_discount_count > 0:
        raise ValueError(
            f"Found {invalid_discount_count:,} rows with invalid discounts."
        )

    # Recalculate gross revenue from the original historical sales fields.
    # Formula: historical unit price multiplied by quantity sold.
    expected_gross_revenue = (
        data["UnitPrice"] * data["Quantity"]
    ).round(2)

    # Recalculate the expected monetary value of the discount.
    # Northwind stores Discount as a proportion, such as 0.20 for 20%.
    expected_discount_amount = (
        expected_gross_revenue * data["Discount"]
    ).round(2)

    # Recalculate sales revenue after applying the discount.
    expected_net_revenue = (
        expected_gross_revenue - expected_discount_amount
    ).round(2)

    # Relate each transformed financial column to its expected calculation.
    expected_financial_values = {
        "GrossRevenue": expected_gross_revenue,
        "DiscountAmount": expected_discount_amount,
        "NetRevenue": expected_net_revenue,
    }

    # Validate the three financial columns using the same comparison process.
    for column_name, expected_values in expected_financial_values.items():

        # Calculate the absolute difference between actual and expected values.
        difference = (
            data[column_name] - expected_values
        ).abs()

        # Allow a difference of approximately one cent to account for
        # floating-point representation and monetary rounding.
        invalid_value_count = (difference > 0.011).sum()

        # Stop the pipeline and identify the affected financial column.
        if invalid_value_count > 0:
            raise ValueError(
                f"Found {invalid_value_count:,} inconsistent values "
                f"in {column_name}."
            )