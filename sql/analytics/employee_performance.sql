-- Analyze employee sales and order-delivery performance.
-- Final granularity: one row represents one employee.

WITH employee_orders AS (
    SELECT
        EmployeeID,
        EmployeeFullName,
        OrderID,

        -- Collapse repeated order-level dates into one order record.
        MAX(RequiredDate) AS RequiredDate,
        MAX(ShippedDate) AS ShippedDate,

        -- Aggregate the product lines belonging to each order.
        SUM(Quantity) AS OrderUnitsSold,
        ROUND(SUM(GrossRevenue), 2) AS OrderGrossRevenue,
        ROUND(SUM(DiscountAmount), 2) AS OrderDiscountAmount,
        ROUND(SUM(NetRevenue), 2) AS OrderNetRevenue

    FROM sales_order_lines

    -- Produce one row per employee and order.
    GROUP BY
        EmployeeID,
        EmployeeFullName,
        OrderID
),

employee_performance AS (
    SELECT
        EmployeeID,
        EmployeeFullName,

        -- COUNT(*) now counts orders because employee_orders has one row per order.
        COUNT(*) AS OrderCount,

        -- Separate completed and pending shipments.
        SUM(
            CASE
                WHEN ShippedDate IS NOT NULL THEN 1
                ELSE 0
            END
        ) AS ShippedOrderCount,

        SUM(
            CASE
                WHEN ShippedDate IS NULL THEN 1
                ELSE 0
            END
        ) AS UnshippedOrderCount,

        -- Aggregate employee-level sales metrics.
        SUM(OrderUnitsSold) AS UnitsSold,
        ROUND(SUM(OrderGrossRevenue), 2) AS GrossRevenue,
        ROUND(SUM(OrderDiscountAmount), 2) AS DiscountAmount,
        ROUND(SUM(OrderNetRevenue), 2) AS NetRevenue,

        -- Calculate average revenue per complete order.
        ROUND(AVG(OrderNetRevenue), 2) AS AverageOrderValue,

        -- Calculate on-time delivery among shipped orders.
        ROUND(
            100.0
            * SUM(
                CASE
                    WHEN ShippedDate IS NOT NULL
                         AND DATE(ShippedDate) <= DATE(RequiredDate)
                    THEN 1
                    ELSE 0
                END
            )
            / NULLIF(
                SUM(
                    CASE
                        WHEN ShippedDate IS NOT NULL THEN 1
                        ELSE 0
                    END
                ),
                0
            ),
            2
        ) AS OnTimeShipmentPercent

    FROM employee_orders

    -- Produce one row for each employee.
    GROUP BY
        EmployeeID,
        EmployeeFullName
),

ranked_employees AS (
    SELECT
        EmployeeID,
        EmployeeFullName,
        OrderCount,
        ShippedOrderCount,
        UnshippedOrderCount,
        UnitsSold,
        GrossRevenue,
        DiscountAmount,
        NetRevenue,
        AverageOrderValue,
        OnTimeShipmentPercent,

        -- Rank employees by total net revenue.
        DENSE_RANK() OVER (
            ORDER BY NetRevenue DESC
        ) AS RevenueRank

    FROM employee_performance
)

SELECT
    EmployeeID,
    EmployeeFullName,
    OrderCount,
    ShippedOrderCount,
    UnshippedOrderCount,
    UnitsSold,
    GrossRevenue,
    DiscountAmount,
    NetRevenue,
    AverageOrderValue,
    OnTimeShipmentPercent,
    RevenueRank

FROM ranked_employees

ORDER BY
    RevenueRank,
    EmployeeFullName;