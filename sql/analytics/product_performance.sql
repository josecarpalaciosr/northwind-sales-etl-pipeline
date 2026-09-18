-- Analyze product performance and revenue contribution by category.
-- Granularity: one row represents one product.

WITH product_performance AS (
    SELECT
        CategoryID,
        CategoryName,
        ProductID,
        ProductName,

        -- Count the unique orders containing each product.
        COUNT(DISTINCT OrderID) AS OrderCount,

        -- Aggregate product quantities and financial metrics.
        SUM(Quantity) AS UnitsSold,
        ROUND(SUM(GrossRevenue), 2) AS GrossRevenue,
        ROUND(SUM(DiscountAmount), 2) AS DiscountAmount,
        ROUND(SUM(NetRevenue), 2) AS NetRevenue

    FROM sales_order_lines

    -- Produce one result row for each product.
    GROUP BY
        CategoryID,
        CategoryName,
        ProductID,
        ProductName
),

ranked_products AS (
    SELECT
        CategoryID,
        CategoryName,
        ProductID,
        ProductName,
        OrderCount,
        UnitsSold,
        GrossRevenue,
        DiscountAmount,
        NetRevenue,

        -- Calculate each product's contribution to its category revenue.
        ROUND(
            NetRevenue
            / NULLIF(
                SUM(NetRevenue) OVER (
                    PARTITION BY CategoryID
                ),
                0
            )
            * 100,
            2
        ) AS CategoryRevenueSharePercent,

        -- Rank products independently inside each category.
        DENSE_RANK() OVER (
            PARTITION BY CategoryID
            ORDER BY NetRevenue DESC
        ) AS RevenueRankWithinCategory,

        -- Rank products across the complete analytical dataset.
        DENSE_RANK() OVER (
            ORDER BY NetRevenue DESC
        ) AS OverallRevenueRank

    FROM product_performance
)

SELECT
    CategoryID,
    CategoryName,
    ProductID,
    ProductName,
    OrderCount,
    UnitsSold,
    GrossRevenue,
    DiscountAmount,
    NetRevenue,
    CategoryRevenueSharePercent,
    RevenueRankWithinCategory,
    OverallRevenueRank

FROM ranked_products

ORDER BY
    OverallRevenueRank,
    CategoryName,
    ProductName;