-- Analyze monthly sales performance and month-over-month growth.
-- Granularity: one row represents one calendar month.

WITH monthly_sales AS (
    SELECT
        -- Convert every order date into the first day of its month.
        DATE(OrderDate, 'start of month') AS SalesMonth,

        -- Count unique orders instead of individual product lines.
        COUNT(DISTINCT OrderID) AS OrderCount,

        -- Calculate the total number of units sold.
        SUM(Quantity) AS UnitsSold,

        -- Aggregate the financial metrics for the month.
        ROUND(SUM(GrossRevenue), 2) AS GrossRevenue,
        ROUND(SUM(DiscountAmount), 2) AS DiscountAmount,
        ROUND(SUM(NetRevenue), 2) AS NetRevenue

    FROM sales_order_lines

    -- Produce one aggregated record for each calendar month.
    GROUP BY DATE(OrderDate, 'start of month')
),

monthly_sales_with_previous AS (
    SELECT
        monthly_sales.SalesMonth,
        monthly_sales.OrderCount,
        monthly_sales.UnitsSold,
        monthly_sales.GrossRevenue,
        monthly_sales.DiscountAmount,
        monthly_sales.NetRevenue,

        -- Retrieve the previous month's revenue for growth calculation.
        LAG(NetRevenue) OVER (
            ORDER BY SalesMonth
        ) AS PreviousMonthNetRevenue

    FROM monthly_sales
)

SELECT
    SalesMonth,
    OrderCount,
    UnitsSold,
    GrossRevenue,
    DiscountAmount,
    NetRevenue,
    PreviousMonthNetRevenue,

    -- Calculate percentage growth relative to the previous month.
    ROUND(
        (
            NetRevenue - PreviousMonthNetRevenue
        )
        / NULLIF(PreviousMonthNetRevenue, 0)
        * 100,
        2
    ) AS MonthOverMonthGrowthPercent

FROM monthly_sales_with_previous

ORDER BY SalesMonth;