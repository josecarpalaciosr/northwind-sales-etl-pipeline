-- Analyze sales performance across discount ranges.
-- Granularity: one row represents one discount band.

WITH categorized_sales AS (
    SELECT
        OrderID,
        ProductID,
        Quantity,
        Discount,
        GrossRevenue,
        DiscountAmount,
        NetRevenue,

        -- Assign each sales line to a descriptive discount range.
        CASE
            WHEN Discount = 0 THEN 'No discount'
            WHEN Discount <= 0.10 THEN 'Low discount (0-10%)'
            WHEN Discount <= 0.20 THEN 'Medium discount (10-20%)'
            ELSE 'High discount (>20%)'
        END AS DiscountBand,

        -- Create a numeric value for logical report ordering.
        CASE
            WHEN Discount = 0 THEN 1
            WHEN Discount <= 0.10 THEN 2
            WHEN Discount <= 0.20 THEN 3
            ELSE 4
        END AS DiscountBandOrder

    FROM sales_order_lines
),

discount_performance AS (
    SELECT
        DiscountBand,
        DiscountBandOrder,

        -- Count sales activity inside each discount range.
        COUNT(*) AS SalesLineCount,
        COUNT(DISTINCT OrderID) AS OrderCount,
        SUM(Quantity) AS UnitsSold,

        -- Calculate the simple average line-discount percentage.
        ROUND(
            AVG(Discount) * 100,
            2
        ) AS AverageDiscountPercent,

        -- Aggregate financial metrics for the discount range.
        ROUND(SUM(GrossRevenue), 2) AS GrossRevenue,
        ROUND(SUM(DiscountAmount), 2) AS DiscountAmount,
        ROUND(SUM(NetRevenue), 2) AS NetRevenue,

        -- Calculate the revenue-weighted effective discount rate.
        ROUND(
            SUM(DiscountAmount)
            / NULLIF(SUM(GrossRevenue), 0)
            * 100,
            2
        ) AS EffectiveDiscountRatePercent

    FROM categorized_sales

    GROUP BY
        DiscountBand,
        DiscountBandOrder
)

SELECT
    DiscountBand,
    SalesLineCount,
    OrderCount,
    UnitsSold,
    AverageDiscountPercent,
    GrossRevenue,
    DiscountAmount,
    NetRevenue,
    EffectiveDiscountRatePercent,

    -- Calculate each band's contribution to total net revenue.
    ROUND(
        NetRevenue
        / NULLIF(
            SUM(NetRevenue) OVER (),
            0
        )
        * 100,
        2
    ) AS GlobalNetRevenueSharePercent

FROM discount_performance

ORDER BY DiscountBandOrder;