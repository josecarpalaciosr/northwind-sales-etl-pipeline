# Northwind Sales: Executive Decision Brief

This brief translates the validated analytical dataset into management actions.
It separates exact observations from estimates and avoids causal claims that the
available data cannot support.

## Executive decision table

| Priority | Verified signal | Business interpretation | Recommended decision | KPI or trigger |
|---|---|---|---|---|
| P1 — Improve delivery reliability | 12,719 of 16,261 shipped orders arrived on time (**78.22%**); 3,542 were late by **7.37 days on average**. The three shippers are tightly grouped at 78.00%–78.33%. | The service gap appears systemic rather than isolated to one carrier. Persistent lateness can put repeat revenue at risk even though returns and satisfaction are not available. | Establish an on-time-delivery improvement program by country and process stage. Review required-date setting, dispatch lead time, carrier handoff, and exception handling before changing carriers. | Raise on-time shipment rate to **85% first**, then **90%**. Reaching 90% on the historical shipped-order base would require 1,916 additional on-time orders. |
| P1 — Investigate the October demand slowdown correctly | October 2023 contains data only through October 28. Against October 1–28, 2022, revenue fell **14.81%**, orders fell **18.10%**, units fell **15.83%**, while average order value rose **4.02%**. | The shortfall is primarily order and unit volume, not order value. The raw dashboard comparisons of -17.53% MoM and -21.36% YoY mix incomplete and complete periods and should not be the sole decision signal. | Add a data-coverage indicator and same-day-of-month comparisons. Diagnose lost order volume by country, customer, and product before considering pricing actions. | Comparable-period revenue, orders, units, and AOV; latest complete date; days loaded versus days in month. |
| P2 — Manage the country portfolio | The top five countries produce **55.06%** of total revenue. For January–September 2023 versus the same 2022 period, gains of **$3.91M** were partly offset by losses of **$2.78M**, leaving **+$1.13M** net. USA (+$0.83M), Venezuela (+$0.78M), Brazil (+$0.69M), and Germany (+$0.57M) led gains; UK (-$0.86M) led declines. | Overall growth hides materially different market trajectories. A single global growth rate is not sufficient for resource allocation. | Protect and replicate growth in the leading gain markets while creating a UK recovery review covering customers, products, and order frequency. Treat high percentage growth in small markets as a signal to validate, not automatic proof of scale. | Country revenue bridge, order count, AOV, customer retention, and country share. |
| P2 — Optimize the product mix | The top product contributes **11.88%** and the top ten contribute **39.47%** of revenue. All eight categories grew in January–September 2023, but 18 of 77 products declined. Beverages remains the largest category at **20.55%** of total revenue yet had the slowest category growth at **1.07%**. | Portfolio growth is broad at category level but uneven at SKU level. The leading product concentration is meaningful but not excessive. | Protect availability of high-revenue products, review the 18 declining products, and test whether winners can be expanded across strong countries. Do not discontinue products using revenue alone; margin and inventory data are required. | Product/category revenue, units, revenue per unit, availability, margin, and country-product growth. |
| P2 — Plan for recurring seasonality | Across complete years 2013–2022, December revenue averaged **8.39% above** the monthly baseline; February averaged **10.84% below** it. May, August, and July were also above average. | Capacity and working-capital needs are predictably uneven during the year. | Align inventory, staffing, and carrier capacity with the seasonal pattern, then compare actuals with a seasonal baseline rather than a flat monthly target. | Seasonal index, forecast error, stockouts, fulfillment capacity, and on-time delivery by month. |
| P3 — Preserve customer diversification | The largest customer contributes **1.37%** of revenue and the top ten contribute **12.46%**. | Customer concentration risk is low even though geographic concentration is material. | Maintain broad account coverage. Use customer-level alerts for sudden declines, but manage strategic concentration primarily by country and product. | Top-10 customer share, active customers, order frequency, retention, and customer revenue change. |
| P3 — Do not overinterpret discounts | Only 838 of 609,283 lines (**0.1375%**) contain a discount, representing **0.1149%** of net revenue. Total recorded discount cost is **$88.7K**. | The sample is too small and non-random to estimate discount effectiveness or causality. | Keep the current dashboard descriptive. If management wants a promotion strategy, run a controlled pilot and capture margin, baseline demand, and customer eligibility. | Incremental revenue and gross margin versus control; redemption and repeat purchase rates. |

## Reconciled reporting baseline

The analytical SQLite table and the exported Power BI CSV were independently
reconciled to the same totals.

| Control | Validated result |
|---|---:|
| Coverage | 2012-07-10 through 2023-10-28 |
| Sales-order lines | 609,283 |
| Unique order/product keys | 609,283 |
| Duplicate order/product keys | 0 |
| Orders | 16,282 |
| Products | 77 |
| Customers | 93 |
| Customer countries | 22 |
| Units sold | 15,538,602 |
| Gross revenue | $448,475,298.72 |
| Discount amount | $88,665.57 |
| Net revenue | $448,386,633.15 |
| Average order value | $27,538.79 |
| Rolling 12-month revenue, Nov 2022–Oct 2023 | $40,082,662.63 |

## Growth and trend validation

### Long-term baseline

The complete calendar years 2013–2022 averaged **$39.65M** in annual net
revenue, ranging from **$38.33M** to **$41.42M**. Revenue grew at only a
**0.31% compound annual rate** from 2013 to 2022. This is a stable business
baseline rather than evidence of sustained structural growth.

### Current comparable period

January–September 2023 versus January–September 2022 shows:

| Metric | Jan–Sep 2022 | Jan–Sep 2023 | Change |
|---|---:|---:|---:|
| Net revenue | $28,996,306.94 | $30,131,125.65 | +3.91% |
| Orders | 995 | 1,037 | +4.22% |
| Units sold | 1,005,192 | 1,041,384 | +3.60% |
| Average order value | $29,142.02 | $29,056.05 | -0.29% |

The revenue increase was driven by more orders and units, while order value was
essentially flat. This supports a volume-led, not price-led, growth narrative.

### October 2023 coverage warning

October 2023 ends on day 28. The dashboard's raw -17.53% month-over-month and
-21.36% year-over-year values are mathematically correct for their current
filters, but the YoY value compares a partial October 2023 with all of October
2022. The fairer October 1–28 comparison is:

| Metric | Oct 1–28, 2022 | Oct 1–28, 2023 | Change |
|---|---:|---:|---:|
| Net revenue | $3,431,658.79 | $2,923,364.35 | -14.81% |
| Orders | 116 | 95 | -18.10% |
| Units sold | 117,635 | 99,014 | -15.83% |
| Average order value | $29,583.27 | $30,772.26 | +4.02% |

At the October 1–28 calendar-day run rate, a simple full-month projection is
approximately **$3.24M**. This is an estimate, not a validated forecast, and
should not replace a proper time-series model.

## Market and portfolio details

### Country concentration

| Country | Total net revenue | Share |
|---|---:|---:|
| USA | $62,601,564.85 | 13.96% |
| France | $53,323,305.76 | 11.89% |
| Germany | $51,195,766.82 | 11.42% |
| Brazil | $45,801,779.28 | 10.21% |
| UK | $33,959,254.81 | 7.57% |
| **Top five** | **$246,881,671.52** | **55.06%** |

The top ten countries account for **76.62%** of revenue. Country-level planning
therefore matters more than customer concentration alone.

### Product concentration

| Product | Category | Total net revenue | Share |
|---|---|---:|---:|
| Côte de Blaye | Beverages | $53,265,895.24 | 11.88% |
| Thüringer Rostbratwurst | Meat/Poultry | $24,623,469.22 | 5.49% |
| Mishi Kobe Niku | Meat/Poultry | $19,423,037.50 | 4.33% |
| Sir Rodney's Marmalade | Confections | $16,653,807.36 | 3.71% |
| Carnarvon Tigers | Seafood | $12,604,671.88 | 2.81% |
| **Top five** |  | **$126,570,881.20** | **28.23%** |

The top ten products account for **39.47%** and the top twenty for **56.59%**
of revenue. Because revenue per unit varies widely, units alone should not be
used to rank commercial importance.

## Operations validation

| Metric | Result |
|---|---:|
| Orders | 16,282 |
| Shipped orders | 16,261 |
| Unshipped orders | 21 |
| On-time shipped orders | 12,719 |
| Late shipped orders | 3,542 |
| On-time shipment rate | 78.22% |
| Average delay among late orders | 7.37 days |
| Maximum delay | 27 days |

The 2023 on-time rate is **76.50%**, essentially unchanged from **76.55%** in
2022. The absence of improvement makes service reliability the clearest
operational intervention in the current data.

## Interpretation limits

- Northwind is a sample dataset, so the findings demonstrate analytical method
  and decision framing rather than a claim about a real operating company.
- 2012 and 2023 are partial years. Full-year trend comparisons use 2013–2022;
  current performance uses matched January–September periods.
- October 2023 is incomplete. Every current-month comparison should display the
  latest loaded date or use a same-day-of-month benchmark.
- The dataset does not contain cost of goods, product margin, inventory,
  stockouts, returns, customer satisfaction, marketing spend, acquisition cost,
  or management targets. Profitability, churn, and causal promotion effects
  therefore cannot be concluded from this model.
- Revenue and shipment relationships are descriptive. They do not prove that a
  country, employee, shipper, product, or discount caused the observed result.

## Recommended next analytical increment

The highest-value extension is an **exception-management page**, not another
general overview. It should combine:

1. Data freshness and period-completeness indicators.
2. A revenue bridge showing country and product contributors to change.
3. Late-order volume, on-time rate, and average days late by country and shipper.
4. A management target selector for service level and the gap to target.
5. Drill-through from a declining country to affected customers and products.

This turns the report from a descriptive dashboard into a decision workflow:
identify the variance, locate its drivers, assign an owner, and track recovery.
