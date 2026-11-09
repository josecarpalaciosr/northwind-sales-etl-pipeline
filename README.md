# Northwind Sales ETL Pipeline

[![Continuous Integration](https://github.com/josecarpalaciosr/northwind-sales-etl-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/josecarpalaciosr/northwind-sales-etl-pipeline/actions/workflows/ci.yml)

A local batch ETL pipeline that extracts Northwind sales data from SQLite, transforms and validates 609,283 sales order lines using Python, SQL, and Pandas, and loads the results into an analytical SQLite database.

## Project Status

The core ETL pipeline is complete and covered by automated tests.

- ✅ Sales data extraction
- ✅ Data cleaning and financial transformations
- ✅ Structural and business-rule validation
- ✅ Analytical SQLite database loading
- ✅ Automated tests with pytest
- ✅ Structured application logging
- ✅ Continuous integration with GitHub Actions
- ✅ Project documentation
- ✅ Reusable analytical SQL queries
- ✅ Automated analytical integration and semantic tests
- ✅ Reproducible centralized fact export for Power BI
- ✅ Four-page Power BI dashboard and semantic model
- 📋 Docker and PostgreSQL migration planned

## Project Overview

This project demonstrates a complete local batch ETL workflow using the Northwind transactional database as its source. The pipeline converts operational sales records into a clean, validated, and query-ready analytical dataset.

The workflow extracts sales order lines with SQL, transforms and enriches them with Pandas, applies structural and business-rule validations, and performs a full-refresh load into a separate analytical SQLite database. Automated tests, structured logging, and continuous integration support reliability and maintainability.

The analytical database provides two independent downstream outputs. A reusable SQL analytics layer supplies tested reference analyses for monthly, product, country, employee, and discount performance. Separately, a centralized sales-order-line fact dataset provides the single reporting source for Power BI. The SQL query results are not exported to or consumed by Power BI.

## Pipeline Architecture

```mermaid
flowchart LR
    A[(Northwind SQLite)] --> B[SQL Extraction]
    B --> C[Pandas Transformation]
    C --> D[Data Validation]
    D --> E[(Analytics SQLite)]
    E --> F[Reference SQL Analytics]
    F --> G[Automated SQL Tests]
    E --> H[Central Fact CSV]
    H --> I[Power BI]
```

## Transformation Logic

The transformation stage cleans source fields and creates analytical attributes without modifying the original extracted DataFrame.

| Transformation | Purpose |
|---|---|
| Convert ISO 8601 date strings to Pandas datetime values | Enable reliable date filtering, grouping, and time-based analysis |
| Replace missing customer countries with `Unknown` | Preserve sales records while assigning an explicit analytical category |
| Remove surrounding spaces from employee names | Standardize inconsistent source text |
| Create `EmployeeFullName` | Provide a reporting-friendly employee attribute |
| Calculate financial metrics | Produce gross revenue, discount amount, and net revenue for every sales line |

The financial metrics are calculated as follows:

- `GrossRevenue = UnitPrice × Quantity`
- `DiscountAmount = GrossRevenue × Discount`
- `NetRevenue = GrossRevenue − DiscountAmount`

All monetary results are rounded to two decimal places.

## Analytical SQL Layer

The processed `sales_order_lines` table supports a collection of reusable analytical SQL queries stored in `sql/analytics/`.

| Query | Business purpose | Main SQL concepts |
|---|---|---|
| `monthly_sales_performance.sql` | Analyze monthly revenue trends and month-over-month growth | CTEs, aggregation, `LAG()`, window functions |
| `product_performance.sql` | Compare product revenue, category contribution, and product rankings | Partitioned window functions, `DENSE_RANK()` |
| `country_performance.sql` | Measure customer-country revenue, average order value, and global contribution | Distinct counts, global window calculations, ranking |
| `employee_performance.sql` | Evaluate employee sales, average order value, and on-time shipment performance | Multi-level aggregation, conditional aggregation, ranking |
| `discount_performance.sql` | Compare revenue and effective discount rates across discount bands | `CASE`, conditional grouping, global revenue share |

The queries operate on the validated analytical table rather than directly on the transactional Northwind schema. They are retained as independently tested reference analyses that demonstrate reusable analytical SQL and provide benchmark results for validating reporting metrics.

Power BI does not consume the results of these five queries. It uses the centralized `sales_order_line_fact.csv` dataset exported directly from the validated `sales_order_lines` table.

The analytical queries include:

- Monthly gross, discount, and net revenue.
- Month-over-month net revenue growth.
- Product rankings within categories and across the complete catalog.
- Country-level revenue contribution and average order value.
- Employee revenue and on-time shipment performance.
- Discount-band utilization, effective rates, and revenue contribution.

## Data Quality Validation

The pipeline validates transformed data before loading it into the analytical database.

| Validation rule | Reason |
|---|---|
| Dataset must not be empty | Prevent loading an unusable analytical table |
| Required columns must exist | Confirm that the expected schema was produced |
| Required values must not be null | Prevent incomplete identifiers and financial calculations |
| `OrderID` and `ProductID` must be unique together | Preserve one record per original sales order line |
| Quantity must be greater than zero | Reject sales lines without a valid sold quantity |
| Unit price must not be negative | Prevent impossible historical prices |
| Discount must be between 0 and 1 | Confirm that discounts are valid proportions |
| Financial metrics must match recalculated values | Detect incorrect revenue or discount calculations |

The validation stage raises a descriptive `ValueError` immediately when a rule fails, preventing invalid data from reaching the analytical database.

## Technology Stack

| Technology | Role in the project |
|---|---|
| Python 3.11+ | ETL orchestration and application logic |
| Pandas | Data extraction results, transformations, and validation |
| SQL | Relational extraction and analytical database objects |
| SQLite | Transactional source and analytical target databases |
| pytest | Automated testing of transformation, validation, loading, analytical SQL, and dataset exports |
| Power BI Desktop | Interactive business reporting and analytical visualization |
| Python logging | Pipeline execution records and error traceability |
| GitHub Actions | Continuous integration across supported Python versions |
| Git and GitHub | Version control, feature branches, and pull-request workflow |

## Project Structure

```text
northwind-sales-etl-pipeline/
├── .github/
│   └── workflows/
│       └── ci.yml
├── data/
│   ├── exports/
│   │   └── sales_order_line_fact.csv  # Generated locally; not versioned
│   ├── processed/
│   └── raw/
│       └── northwind.db
├── docs/
│   ├── NORTHWIND_SQLITE_LICENSE.txt
│   ├── power_bi_semantic_model.md
│   └── source_erd.md
├── logs/
├── reports/
│   ├── figures/
│   └── Northwind_Sales_Analytics_v2_final.pbix
├── sql/
│   ├── analytics/
│   │   ├── country_performance.sql
│   │   ├── discount_performance.sql
│   │   ├── employee_performance.sql
│   │   ├── monthly_sales_performance.sql
│   │   └── product_performance.sql
│   └── extraction/
│       └── sales_order_lines.sql
├── src/
│   └── northwind_etl/
│       ├── __init__.py
│       ├── extract.py
│       ├── export_analytics.py
│       ├── inspect_database.py
│       ├── load.py
│       ├── logging_config.py
│       ├── pipeline.py
│       ├── transform.py
│       └── validate.py
├── tests/
│   ├── test_analytics.py
│   ├── test_export_analytics.py
│   ├── test_load.py
│   ├── test_transform.py
│   └── test_validate.py
├── .gitignore
├── pyproject.toml
└── README.md
```

- `.github/workflows/ci.yml`: runs the automated test suite with GitHub Actions.
- `data/raw/`: contains the original Northwind SQLite database.
- `data/processed/`: receives the analytical database generated by the pipeline.
- `data/exports/`: receives the reproducible centralized fact dataset generated locally for Power BI. The large CSV is intentionally not versioned.
- `docs/`: contains the source database license and entity-relationship documentation.
- `logs/`: receives generated pipeline execution logs.
- `reports/figures/`: is reserved for generated analytical visualizations.
- `reports/Northwind_Sales_Analytics_v2_final.pbix`: contains the completed four-page interactive Power BI report.
- `sql/extraction/`: contains SQL used to extract transactional sales data.
- `sql/analytics/`: contains reusable business-oriented SQL queries for monthly, product, country, employee, and discount analysis.
- `src/northwind_etl/`: contains the installable ETL package.
- `tests/`: contains unit, integration, and semantic tests for the ETL pipeline, analytical SQL layer, and reporting dataset exports.

## Installation

### Prerequisites

- Python 3.11 or later
- Git

### Clone the repository

```bash
git clone https://github.com/josecarpalaciosr/northwind-sales-etl-pipeline.git
cd northwind-sales-etl-pipeline
```

### Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install the project

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

The `dev` optional dependency group installs pytest in addition to the runtime dependencies.

## Running the Pipeline

Run the complete ETL pipeline from the repository root:

```bash
python -m northwind_etl.pipeline
```

The command performs the following operations:

1. Verifies that the source database exists.
2. Extracts sales order lines with SQL.
3. Transforms dates, customer countries, employee names, and financial metrics.
4. Confirms that transformation preserved the original row count.
5. Validates structural, business, and financial rules.
6. Loads the validated data into the analytical SQLite database.
7. Records execution details in the terminal and log file.

Generated outputs:

- Analytical database: `data/processed/northwind_analytics.db`
- Execution log: `logs/pipeline.log`

### Inspect the analytical database

After running the pipeline, optionally inspect the generated analytical database, including its tables, columns, indexes, row counts, and sample records:

```bash
python -m northwind_etl.inspect_database
```

This diagnostic command reads `data/processed/northwind_analytics.db` without modifying it. It is useful for manually verifying the generated database or investigating unexpected results, but it is not required during normal pipeline execution.

### Export the Power BI fact dataset

After the analytical database has been created, export the complete validated sales fact table for Power BI:

```bash
python -m northwind_etl.export_analytics
```

The command creates or refreshes the following local file:

```text
data/exports/
└── sales_order_line_fact.csv
```

The export preserves the validated sales-order-line grain: one row for each unique `OrderID` and `ProductID` combination. It contains 609,283 rows and 27 transformed columns and serves as the single fact source for Power BI.

The file is intentionally excluded from Git because it is large and fully reproducible. Run the export command again whenever the analytical database is rebuilt with updated source data.

The completed report is stored at
`reports/Northwind_Sales_Analytics_v2_final.pbix`. It contains four pages:

1. **Executive Overview** for company-level KPIs and market leaders.
2. **Product & Market Performance** for category, product, and volume analysis.
3. **Operations & Discounts** for employee, shipment, and discount performance.
4. **Trends & Growth** for annual, monthly, and rolling revenue trends.

Year, Country, and Category slicers are synchronized across all report pages.
The semantic-model definitions and the calendar-month Rolling 12M benchmark are
documented in [Power BI semantic model notes](docs/power_bi_semantic_model.md).

The complete local workflow is:

```bash
python -m northwind_etl.pipeline
python -m northwind_etl.inspect_database  # Optional diagnostic step
python -m northwind_etl.export_analytics
```

## Automated Testing

The project includes 29 automated tests covering successful behavior and expected failure conditions across the transformation, validation, load, analytical SQL, and dataset-export stages. The analytical SQL tests confirm that every query executes successfully, preserves its expected output schema, and satisfies key business invariants such as revenue shares totaling approximately 100%, rankings starting at one, valid percentage ranges, and correct month-over-month calculations.

| Stage | Tests | Main coverage |
|---|---:|---|
| Analytics | 10 | Query execution, output schemas, monthly growth, revenue shares, rankings, percentage ranges, and discount consistency |
| Export | 3 | Central fact CSV creation, row preservation, deterministic ordering, and clear failures for missing databases or fact tables |
| Transform | 5 | Date conversion, missing-country handling, employee-name cleaning, financial calculations, and preservation of the original DataFrame |
| Validate | 9 | Valid data, empty datasets, missing columns, null values, duplicates, invalid quantities, negative prices, invalid discounts, and inconsistent revenue |
| Load | 2 | Analytical table and index creation, plus repeatable full-refresh loading |
| **Total** | **29** | ETL, analytical SQL, and reporting-export validation |

Run the complete test suite with:

```bash
python -m pytest -v
```

The transformation and validation tests use small representative DataFrames so that individual rules can be verified quickly and independently. Load and export tests use temporary SQLite databases and directories managed by pytest, preventing automated tests from modifying the real analytical database or reporting files. Analytical integration and semantic tests build a temporary analytical database from the source data, execute the actual reference SQL files against it, and validate their output structure and principal business rules.

The analytical SQL tests and the fact-export tests cover separate responsibilities. `test_analytics.py` validates the five reusable reference analyses without creating persistent CSV files. `test_export_analytics.py` validates only the centralized fact dataset consumed by Power BI.

The automated tests do not depend on the locally generated `data/processed/northwind_analytics.db` file. In continuous integration, GitHub Actions checks out the tracked `data/raw/northwind.db` source, and pytest builds the required analytical databases in temporary directories that are discarded after the test session.

## Logging

The pipeline uses Python's standard logging library to record execution progress and failures.

Logs are written to both:

- The terminal for immediate execution feedback.
- `logs/pipeline.log` for persistent local troubleshooting.

The default logging level is `INFO`, which records pipeline stages and dataset dimensions. Detailed previews can use `DEBUG`, while unexpected failures are recorded with their traceback before being raised again.

## Continuous Integration

GitHub Actions automatically runs the complete test suite in clean Ubuntu environments using:

- Python 3.11, the minimum supported version.
- Python 3.14, the current development version.

The workflow runs when:

- A pull request targets `main`.
- Changes are pushed or merged into `main`.
- A user starts it manually with `workflow_dispatch`.

This verifies that the project can be installed and tested outside the developer's local environment. The workflow configuration is stored in `.github/workflows/ci.yml`.

## Data Source

The project uses a SQLite version of the Northwind sample database stored at `data/raw/northwind.db`. Keeping the source database in the repository makes the ETL pipeline reproducible without requiring an external database server.

The generated `data/processed/northwind_analytics.db` database is intentionally not versioned. It can be recreated from the tracked source database and project code by running the pipeline. The large `data/exports/sales_order_line_fact.csv` Power BI dataset is also intentionally not versioned and can be refreshed with the export command.

Additional source documentation:

- [Source database entity-relationship diagram](docs/source_erd.md)
- [Northwind SQLite license information](docs/NORTHWIND_SQLITE_LICENSE.txt)

## Pipeline Results

A successful end-to-end local workflow currently produces:

| Metric | Result |
|---|---:|
| Extracted sales order lines | 609,283 |
| Extracted columns | 23 |
| Transformed sales order lines | 609,283 |
| Transformed columns | 27 |
| Loaded analytical rows | 609,283 |
| Exported Power BI fact rows | 609,283 |
| Exported Power BI fact columns | 27 |
| Automated tests | 29 |
| Analytical indexes | 3 |

The unchanged row count confirms that the transformation preserves sales-line granularity. The four additional transformed columns provide cleaned employee information and calculated financial metrics for analytical use.

## Business Insights

The validated dataset and report support the following portfolio-level findings:

- October 2023 net revenue was **$2.92M**, decreasing **17.53% month over month** and **21.36% year over year**.
- The five leading countries contribute **55.06%** of total net revenue; the United States leads with **13.96%**.
- The ten leading products contribute **39.47%** of total net revenue; Côte de Blaye alone contributes **11.88%**.
- Employee on-time shipment performance ranges from **76.82% to 79.75%**, indicating a measurable operational improvement opportunity.
- **99.89%** of net revenue comes from transactions without a discount. Discounted activity is therefore too limited to infer that discounts cause higher or lower sales.

These findings are descriptive rather than causal and respond dynamically to the synchronized Power BI filters.

## Roadmap

- [x] Build the local SQLite ETL pipeline
- [x] Add structural, business, and financial validation
- [x] Add automated tests
- [x] Add structured logging
- [x] Add continuous integration
- [x] Create complete project documentation
- [x] Add analytical SQL queries
- [x] Add automated tests for the analytical SQL layer
- [x] Add a reproducible centralized fact export for Power BI
- [x] Complete the Power BI dashboard and semantic model
- [ ] Containerize the project with Docker
- [ ] Migrate the analytical database to PostgreSQL
