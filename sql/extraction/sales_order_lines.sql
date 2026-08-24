-- Extract sales order lines from the Northwind source database.
-- Granularity: one row represents one product line within one order.

SELECT
    -- Identifiers for the order and product.
    od.OrderID,
    od.ProductID,

    -- Add the descriptive product name from the Products table.
    p.ProductName,

    -- Order-level dates used for sales and delivery analysis.
    o.OrderDate,
    o.RequiredDate,
    o.ShippedDate,

    -- Destination information recorded for the order.
    o.ShipCity,
    o.ShipCountry,

    -- Identify the category associated with the product.
    p.CategoryID,
    cat.CategoryName,

    -- Identify the supplier associated with the product.
    p.SupplierID,
    s.CompanyName AS SupplierName,

    -- Identify the customer associated with the order.
    o.CustomerID,
    c.CompanyName AS CustomerName,
    c.Country AS CustomerCountry,

    -- Identify the employee responsible for the order.
    o.EmployeeID,
    e.FirstName AS EmployeeFirstName,
    e.LastName AS EmployeeLastName,

    -- Identify the shipping company assigned to the order.
    o.ShipVia AS ShipperID,
    sh.CompanyName AS ShipperName,

    -- Original sales values stored in the order-detail line.
    od.UnitPrice,
    od.Quantity,
    od.Discount

-- Order Details is the main table because it defines the dataset granularity.
FROM "Order Details" AS od

-- Add the order date by matching the foreign key with the Orders primary key.
INNER JOIN Orders AS o
    ON od.OrderID = o.OrderID

-- Preserve every sales line while adding customer information when available (even Customer NULL).
LEFT JOIN Customers AS c
    ON o.CustomerID = c.CustomerID

-- Preserve every sales line while adding the responsible employee when available.
LEFT JOIN Employees AS e
    ON o.EmployeeID = e.EmployeeID

-- Preserve every sales line while adding the assigned shipper when available.
LEFT JOIN Shippers AS sh
    ON o.ShipVia = sh.ShipperID

-- Add product information by matching the foreign key with the Products primary key.
INNER JOIN Products AS p
    ON od.ProductID = p.ProductID

-- Preserve every sales line while adding its product category when available (even Category null).
LEFT JOIN Categories AS cat
    ON p.CategoryID = cat.CategoryID

-- Preserve every sales line while adding its product supplier when available.
LEFT JOIN Suppliers AS s
    ON p.SupplierID = s.SupplierID;