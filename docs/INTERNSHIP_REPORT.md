# Internship Project Report: Retail & Supply Chain Control Tower

**Candidate Role:** Data Analytics Intern  
**Project Title:** Retail & Supply Chain Control Tower  
**Technology Stack:** Python, PostgreSQL, Apache Airflow, Apache Superset, Facebook Prophet, Pandas, SciPy, Scikit-learn, Streamlit, Plotly  

---

## 1. Executive Summary
The **Retail & Supply Chain Control Tower** project addresses the critical challenge of operational visibility across retail supply chains. By integrating transactional databases, automated statistical anomaly detection, AI-driven demand forecasting, and what-if scenario simulations into a centralized control tower, the system empowers inventory managers and executives to transition from reactive firefighting to proactive, data-driven supply chain orchestration.

---

## 2. Business Objectives & Problem Statement
Retail supply chain operations frequently face three major pain points:
1. **Unplanned Stock-Outs**: Leading to lost revenue, degraded customer loyalty, and cart abandonment.
2. **Supplier Lead Time Volatility**: Unpredictable supplier delays disrupting replenishment cycles.
3. **Information Silos**: Transactional sales data, warehouse inventory, and carrier shipment updates isolated across disparate systems without centralized analytics.

The objective was to engineer an automated, scalable data analytics control tower that continuously ingests operational data, computes standardized key performance indicators (KPIs), flags statistical outliers, forecasts 7-day product-level demand, and models disruption scenarios.

---

## 3. Data Architecture & Relational Schema
The underlying data platform is built on PostgreSQL, comprising 11 relational tables and 6 analytical views:

```
+---------------------------------------------------------------------------------------+
|                                    DATA PLATFORM                                      |
+---------------------------------------------------------------------------------------+
| Core Dimensions & Transactions:                                                       |
|   • suppliers (10 suppliers, contact info, reliability scores)                       |
|   • products (100 SKUs, unit costs, retail prices, reorder points, lead times)        |
|   • inventory (on-hand, reserved, available, safety stock, status)                   |
|   • sales_orders (90-day daily transactions, 3,663 orders across regions & channels)  |
|   • shipments (purchase order fulfillments, actual vs expected dates, delay days)     |
|                                                                                       |
| Analytical & Forecasting Engine:                                                      |
|   • kpi_metrics (historical top-line snapshots: Stockout %, OTD %, Lead time, DOI)   |
|   • product_kpis (product-level burn rate and days of inventory runway)               |
|   • anomalies (Z-score detected demand surges & supplier transit delays)              |
|   • demand_forecasts (Prophet 7-day daily forecast points & stockout risk flags)      |
|   • what_if_scenarios (7-day supplier delay vulnerability and shortage modeling)     |
|   • alert_logs (audit log of automated notifications and exception digests)           |
+---------------------------------------------------------------------------------------+
```

---

## 4. Key Performance Indicator (KPI) Results & Insights

The automated engine computes four primary operational metrics:

### 4.1 Stock-Out Rate: `5.0%`
- **Definition**: Percentage of monitored catalog products currently with zero available stock.
- **Result**: Exactly 5 out of 100 products are currently stocked out (`PROD-001` through `PROD-005`).
- **Action**: Automated procurement triggers recommended when stock drops below safety buffer.

### 4.2 On-Time Delivery Percentage (OTD %): `81.6%`
- **Definition**: Proportion of supplier replenishment shipments completed on or before the committed delivery date.
- **Result**: Out of 207 evaluated shipments, 38 experienced delays, yielding an $81.6\%$ fulfillment rate.
- **Action**: Identifies low-performing suppliers (`Pacific Freight & Imports`, `BlueWave Distribution`) requiring vendor review.

### 4.3 Average Supplier Lead Time: `8.15 Days`
- **Definition**: Average turnaround time from purchase order creation to warehouse delivery receipt.
- **Benchmark**: Normalized against contractual targets of 3 to 14 days across supplier tiers.

### 4.4 Portfolio Average Days of Inventory Remaining: `87.5 Days`
- **Definition**: Inventory runway calculated as current stock divided by trailing 30-day average daily demand.
- **Granularity**: Tracked at both individual SKU level and consolidated portfolio level.

---

## 5. Statistical Anomaly Detection (Z-Score Methodology)

Standardized scores ($Z = \frac{x - \mu}{\sigma}$) are calculated to separate random variations from operational disruptions:

1. **Demand Spikes ($Z \ge 2.0$)**:
   - Monitored across daily sales velocity per SKU.
   - 8 critical demand spikes identified (e.g. `PROD-011` surging to 60 units vs. baseline mean of 7.2 units, $Z = 4.51$).
   - Enables marketing and procurement teams to align on promotion-driven surges.

2. **Unexpected Shipment Delays ($Z \ge 2.0$)**:
   - Monitored across shipment lead times and delay durations.
   - 10 extreme shipment delay anomalies identified (e.g. shipment `SHP-5151` delayed by 18 days with lead time of 25 days vs. normal 8.0-day average, $Z = 3.59$).

---

## 6. Predictive Modeling with Facebook Prophet
- **Model Specification**: Additive time-series model incorporating weekly seasonality components ($g(t) + s(t) + \epsilon_t$) with $90\%$ uncertainty intervals.
- **Scale**: Fitted individually across all 100 products over a 7-day forward horizon (700 daily prediction points).
- **Stockout Risk Identification**: By accumulating predicted daily consumption $\sum_{k=1}^7 \hat{y}_{t+k}$ and comparing against current stock, the system flagged **6 products facing imminent stockout** within 7 days, allowing procurement to expedite replenishment prior to customer impact.

---

## 7. What-If Scenario Analysis: 7-Day Supplier Delay Simulation
To evaluate supply chain resilience against logistics disruptions (e.g., port congestion or vendor labor strikes), a 7-day delivery delay was simulated across the entire catalog:
- **Baseline**: 5 products out of stock.
- **Under 7-Day Delay**: Stockouts surge from 5 to **11 products** ($11\%$ of catalog).
- **Projected Deficit**: Total unfulfilled customer demand of **194 units**.
- **Impact Severity Breakdown**:
  - `CRITICAL`: 5 products
  - `HIGH`: 2 products
  - `MEDIUM`: 4 products
  - `LOW`: 12 products
  - `NONE`: 77 products
- **Strategic Takeaway**: Highlights high-velocity items with lean safety buffers that require dynamic buffer stock adjustments.

---

## 8. Dashboard Architecture & Visualizations
The solution provides an executive Control Tower dashboard covering all 10 core analytical views:
1. **Total Products** (100 SKUs)
2. **Current Inventory** (Consolidated on-hand units)
3. **Stock-Out Rate** (Percentage badge with status delta)
4. **On-Time Delivery %** (Fulfillment performance)
5. **Supplier Lead Time** (Mean order-to-dock cycle)
6. **Inventory Health Distribution** (Interactive breakdown of Healthy, Low Stock, and Out of Stock)
7. **Supplier Performance & Delays** (Lead time ranking and delayed shipment logs)
8. **7-Day Prophet Forecast Curves** (Interactive daily trajectories with confidence bands and remaining stock curves)
9. **Z-Score Anomaly Outlier Scatter Plot** (Severity-coded event stream)
10. **What-If Scenario Vulnerability Matrix** (Shortage unit bar charts and impact classification)

---

## 9. Conclusion & Recommendations
1. **Dynamic Safety Stock**: Transition from static reorder points to dynamic buffers calculated from Prophet forecasted demand variance.
2. **Supplier Scorecard Enforcement**: Reallocate procurement volumes to suppliers demonstrating $\ge 95\%$ on-time delivery reliability.
3. **Automated Triggering**: Leverage the hourly Airflow orchestration to automatically generate draft replenishment purchase orders when stockout risk is detected.

