# Northwind Source Data Model

This document describes the main relationships in the operational Northwind SQLite database used as the source of the ETL pipeline.

## Core Sales Model

```mermaid
erDiagram
    CUSTOMERS ||--o{ ORDERS : places
    EMPLOYEES ||--o{ ORDERS : handles
    SHIPPERS ||--o{ ORDERS : ships
    ORDERS ||--|{ ORDER_DETAILS : contains
    PRODUCTS ||--o{ ORDER_DETAILS : appears_in
    CATEGORIES ||--o{ PRODUCTS : classifies
    SUPPLIERS ||--o{ PRODUCTS : supplies

    CUSTOMERS {
        string CustomerID PK
        string CompanyName
        string Country
    }

    EMPLOYEES {
        int EmployeeID PK
        string FirstName
        string LastName
        int ReportsTo FK
    }

    SHIPPERS {
        int ShipperID PK
        string CompanyName
    }

    ORDERS {
        int OrderID PK
        string CustomerID FK
        int EmployeeID FK
        datetime OrderDate
        datetime RequiredDate
        datetime ShippedDate
        int ShipVia FK
        numeric Freight
    }

    ORDER_DETAILS {
        int OrderID PK, FK
        int ProductID PK, FK
        numeric UnitPrice
        int Quantity
        real Discount
    }

    PRODUCTS {
        int ProductID PK
        string ProductName
        int SupplierID FK
        int CategoryID FK
        numeric UnitPrice
        int UnitsInStock
        int UnitsOnOrder
        int ReorderLevel
    }

    CATEGORIES {
        int CategoryID PK
        string CategoryName
    }

    SUPPLIERS {
        int SupplierID PK
        string CompanyName
        string Country
    }
```

`ORDER_DETAILS` represents the source table named `"Order Details"` in SQLite. The underscore is used in the diagram to avoid spaces in the entity identifier.

## Supporting Relationships

```mermaid
erDiagram
    EMPLOYEES o|--o{ EMPLOYEES : manages
    EMPLOYEES ||--o{ EMPLOYEE_TERRITORIES : assigned_to
    TERRITORIES ||--o{ EMPLOYEE_TERRITORIES : includes
    REGIONS ||--o{ TERRITORIES : contains
    CUSTOMERS ||--o{ CUSTOMER_CUSTOMER_DEMO : classified_as
    CUSTOMER_DEMOGRAPHICS ||--o{ CUSTOMER_CUSTOMER_DEMO : describes
```

The customer demographic tables currently contain no records and are not required by the initial sales ETL pipeline.

## Key Relationship Types

- One customer can place many orders.
- One employee can handle many orders.
- One shipper can deliver many orders.
- One order contains many order-detail lines.
- One product can appear in many order-detail lines.
- One category can contain many products.
- One supplier can supply many products.
- One employee can report to another employee.
- Employees and territories have a many-to-many relationship through `EmployeeTerritories`.

## ETL Relevance

The initial ETL pipeline will focus on the core sales tables:

- `Orders`
- `"Order Details"`
- `Products`
- `Categories`
- `Customers`
- `Employees`
- `Shippers`
- `Suppliers`

These relationships determine the joins, referential-integrity validations, dimensional model, and table-loading order used by the pipeline.