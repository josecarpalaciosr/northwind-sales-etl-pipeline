# Northwind Source Database ER Diagram

> The diagrams show the relationships and columns relevant to the initial sales ETL pipeline, not every physical column in the source database.

## Core Sales Relationships

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
        string ShipCity
        string ShipCountry
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

## Supporting Relationships

```mermaid
erDiagram
    REGIONS ||--o{ TERRITORIES : contains
    TERRITORIES ||--o{ EMPLOYEE_TERRITORIES : includes
    EMPLOYEES ||--o{ EMPLOYEE_TERRITORIES : assigned_to
    EMPLOYEES o|--o{ EMPLOYEES : manages

    CUSTOMER_DEMOGRAPHICS ||--o{ CUSTOMER_CUSTOMER_DEMO : describes
    CUSTOMERS ||--o{ CUSTOMER_CUSTOMER_DEMO : classified_as

    REGIONS {
        int RegionID PK
        string RegionDescription
    }

    TERRITORIES {
        string TerritoryID PK
        string TerritoryDescription
        int RegionID FK
    }

    EMPLOYEES {
        int EmployeeID PK
        int ReportsTo FK
    }

    EMPLOYEE_TERRITORIES {
        int EmployeeID PK, FK
        string TerritoryID PK, FK
    }

    CUSTOMER_DEMOGRAPHICS {
        string CustomerTypeID PK
        string CustomerDesc
    }

    CUSTOMERS {
        string CustomerID PK
    }

    CUSTOMER_CUSTOMER_DEMO {
        string CustomerID PK, FK
        string CustomerTypeID PK, FK
    }
```

The customer demographic tables currently contain no records and are not required by the initial sales ETL pipeline.