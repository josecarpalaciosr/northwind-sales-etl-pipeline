"""Transform extracted Northwind sales data."""

import pandas as pd


# Date columns that must be converted from source strings.
DATE_COLUMNS = (
    "OrderDate",
    "RequiredDate",
    "ShippedDate",
)


def transform_sales_order_lines(
    sales_order_lines: pd.DataFrame,
) -> pd.DataFrame:
    """Clean and enrich the extracted sales order lines."""

    # Work on a copy to avoid modifying the extracted DataFrame directly.
    transformed_data = sales_order_lines.copy()

    # Convert every source date column from ISO 8601 strings to Pandas datetime.
    for column_name in DATE_COLUMNS:
        transformed_data[column_name] = pd.to_datetime(
            transformed_data[column_name],
            format="ISO8601",
            errors="raise",
        )
        
    # Replace missing customer countries with an explicit analytical label.
    transformed_data["CustomerCountry"] = transformed_data["CustomerCountry"].fillna("Unknown")

    # Remove surrounding spaces from employee names.
    employee_first_name = transformed_data["EmployeeFirstName"].str.strip()
    employee_last_name = transformed_data["EmployeeLastName"].str.strip()

    # Combine the employee's first and last names.
    transformed_data["EmployeeFullName"] = (
        employee_first_name + " " + employee_last_name
    )

    # Calculate revenue before applying the line discount.
    gross_revenue = (
        transformed_data["UnitPrice"]
        * transformed_data["Quantity"]
    )

    # Calculate the monetary value deducted from the gross revenue.
    discount_amount = (
        gross_revenue
        * transformed_data["Discount"]
    )

    # Add the calculated monetary metrics to the transformed dataset.
    transformed_data["GrossRevenue"] = gross_revenue.round(2)
    transformed_data["DiscountAmount"] = discount_amount.round(2)
    transformed_data["NetRevenue"] = (
        gross_revenue - discount_amount
    ).round(2)

    return transformed_data