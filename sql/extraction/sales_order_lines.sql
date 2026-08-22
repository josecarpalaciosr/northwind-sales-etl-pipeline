-- Extract sales order lines from the Northwind source database.
-- Granularity: one row represents one product line within one order.

SELECT
    -- Identifiers for the order and product.
    od.OrderID,
    od.ProductID,

    -- Order-level information obtained from the Orders table.
    o.OrderDate,

    -- Original sales values stored in the order-detail line.
    od.UnitPrice,
    od.Quantity,
    od.Discount

-- Order Details is the main table because it defines the dataset granularity.
FROM "Order Details" AS od

-- Add the order date by matching the foreign key with the Orders primary key.
INNER JOIN Orders AS o
    ON od.OrderID = o.OrderID;