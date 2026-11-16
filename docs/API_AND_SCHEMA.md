# 📖 Database Schema & Analytical Data Dictionary

This document provides a comprehensive technical reference for the PostgreSQL relational schema (`supply_chain_control_tower`), including table definitions, column types, relationships, constraints, indices, and analytical views.

---

## 1. Relational Tables Overview

| Table Name | Primary Key | Foreign Keys | Row Count | Purpose |
|---|---|---|---|---|
| `suppliers` | `supplier_id` | *None* | 10 | Stores supplier directory, geographical origin, and reliability scores |
| `products` | `product_id` | `supplier_id` $\to$ `suppliers` | 100 | Retail catalog across 6 merchandise categories with pricing & targets |
| `inventory` | `inventory_id` | `product_id` $\to$ `products` | 100 | Real-time on-hand, reserved, and available stock levels with reorder thresholds |
| `sales_orders` | `order_id` | `product_id` $\to$ `products` | 3,663 | 90-day daily point-of-sale customer order transactions |
| `shipments` | `shipment_id` | `supplier_id`, `product_id` | 233 | Purchase order fulfillment tracking, lead times, transit status & delays |
| `kpi_metrics` | `metric_id` | *None* | Time-series | Historical top-level executive KPIs (Stock-out rate, OTD %, Lead time, DOI) |
| `product_kpis` | `product_id` | `product_id` $\to$ `products` | 100 | Granular product velocity, 30-day average demand, and runway in days |
| `anomalies` | `anomaly_id` | `reference_id` (Polymorphic) | Dynamic (18) | Z-score statistical anomalies (demand surges & unexpected transit delays) |
| `demand_forecasts` | `forecast_id` | `product_id` $\to$ `products` | 700 | Facebook Prophet 7-day future demand projections & stockout risk flags |
| `what_if_scenarios` | `scenario_id` | `product_id`, `supplier_id` | 100 | Simulation results for a +7-day supplier replenishment disruption |
| `alert_logs` | `alert_id` | *None* | Audit Log | Event audit log for email dispatches and exception notices |

---

## 2. Table Column Specifications

### 2.1 `suppliers`
Holds supplier master data, geographic location, and baseline performance.
- `supplier_id` (`VARCHAR(20)`, PK): Unique supplier identifier (e.g., `SUPP-001`).
- `supplier_name` (`VARCHAR(100)`, NOT NULL): Legal business name of the supplier.
- `contact_name` (`VARCHAR(100)`): Primary contact representative.
- `email` (`VARCHAR(100)`): Commercial communication email.
- `phone` (`VARCHAR(50)`): Business telephone number.
- `city` (`VARCHAR(50)`): Origin city (e.g., `Seattle, WA`, `Chicago, IL`).
- `country` (`VARCHAR(50)`, DEFAULT `'USA'`): Country of incorporation.
- `reliability_score` (`NUMERIC(5,2)`, DEFAULT `95.00`): Baseline on-time rating percentage (0.00 to 100.00).
- `created_at` (`TIMESTAMP`, DEFAULT `CURRENT_TIMESTAMP`): Record creation timestamp.

### 2.2 `products`
Master catalog of finished retail goods monitored by the Control Tower.
- `product_id` (`VARCHAR(20)`, PK): Unique SKU code (e.g., `PROD-001`).
- `product_name` (`VARCHAR(150)`, NOT NULL): Commercial brand and item description.
- `category` (`VARCHAR(50)`, NOT NULL): Merchandise grouping (`Electronics`, `Apparel`, `Home Goods`, `Food & Beverage`, `Health & Beauty`, `Sports`).
- `unit_price` (`NUMERIC(10,2)`, NOT NULL): Retail selling price ($USD).
- `cost_price` (`NUMERIC(10,2)`, NOT NULL): Wholesale acquisition cost ($USD).
- `reorder_point` (`INT`, NOT NULL, DEFAULT `50`): Minimum inventory trigger level.
- `target_stock_level` (`INT`, NOT NULL, DEFAULT `250`): Optimal warehouse target quantity.
- `lead_time_days` (`INT`, NOT NULL, DEFAULT `7`): Expected nominal replenishment cycle in days.
- `supplier_id` (`VARCHAR(20)`, FK): Reference to `suppliers(supplier_id)`.
- `created_at` (`TIMESTAMP`, DEFAULT `CURRENT_TIMESTAMP`): Catalog entry timestamp.

### 2.3 `inventory`
Real-time physical and allocated stock tracking per product SKU.
- `inventory_id` (`SERIAL`, PK): Auto-incrementing internal sequence.
- `product_id` (`VARCHAR(20)`, UNIQUE, FK): Reference to `products(product_id)`.
- `current_stock` (`INT`, NOT NULL, DEFAULT `0`): Total physical units on warehouse floor.
- `reserved_stock` (`INT`, NOT NULL, DEFAULT `0`): Units allocated to pending customer orders.
- `available_stock` (`INT`, NOT NULL, DEFAULT `0`): Unencumbered units available for sale (`current_stock - reserved_stock`).
- `reorder_point` (`INT`, NOT NULL, DEFAULT `50`): Reorder threshold.
- `safety_stock` (`INT`, NOT NULL, DEFAULT `30`): Buffer stock to mitigate demand spikes.
- `stock_status` (`VARCHAR(20)`, NOT NULL): Status indicator (`IN_STOCK`, `LOW_STOCK`, `OUT_OF_STOCK`).
- `last_updated` (`TIMESTAMP`, DEFAULT `CURRENT_TIMESTAMP`): Timestamp of latest replenishment or sales deduction.

### 2.4 `sales_orders`
Historical point-of-sale customer transactions over a 90-day historical window.
- `order_id` (`VARCHAR(30)`, PK): Transaction receipt identifier (e.g., `ORD-20260216-0001`).
- `order_date` (`DATE`, NOT NULL): Calendar date order was processed.
- `product_id` (`VARCHAR(20)`, FK): Reference to `products(product_id)`.
- `quantity_ordered` (`INT`, NOT NULL): Volume of units purchased.
- `unit_price` (`NUMERIC(10,2)`, NOT NULL): Retail price at time of sale.
- `total_amount` (`NUMERIC(12,2)`, NOT NULL): Total transaction value (`quantity_ordered * unit_price`).
- `store_id` (`VARCHAR(20)`, DEFAULT `'STORE-01'`): Physical retail outlet or fulfillment facility.
- `customer_region` (`VARCHAR(50)`, DEFAULT `'North America'`): Destination sales territory.
- `created_at` (`TIMESTAMP`, DEFAULT `CURRENT_TIMESTAMP`): Transaction ingest timestamp.

### 2.5 `shipments`
Inbound purchase order shipments dispatched by upstream suppliers.
- `shipment_id` (`VARCHAR(30)`, PK): Bill of lading identifier (e.g., `SHIP-20260216-0001`).
- `supplier_id` (`VARCHAR(20)`, FK): Origin supplier reference.
- `product_id` (`VARCHAR(20)`, FK): Product SKU being replenished.
- `quantity_shipped` (`INT`, NOT NULL): Total units consigned.
- `order_date` (`DATE`, NOT NULL): Date purchase order was issued.
- `expected_delivery_date` (`DATE`, NOT NULL): Contractual SLA delivery deadline.
- `actual_delivery_date` (`DATE`): Recorded warehouse receiving date (`NULL` if in-transit).
- `shipping_status` (`VARCHAR(20)`, NOT NULL): Transit state (`DELIVERED`, `IN_TRANSIT`, `DELAYED`).
- `lead_time_days` (`INT`): Elapsed calendar days from order to delivery.
- `is_delayed` (`BOOLEAN`, DEFAULT `FALSE`): Flagged `TRUE` if `actual_delivery_date > expected_delivery_date` or in-transit and past expected date.
- `delay_days` (`INT`, DEFAULT `0`): Number of calendar days delayed beyond SLA.
- `created_at` (`TIMESTAMP`, DEFAULT `CURRENT_TIMESTAMP`): Record creation timestamp.

### 2.6 `kpi_metrics`
System-wide hourly snapshots of core Control Tower operational indicators.
- `metric_id` (`SERIAL`, PK): Sequential evaluation identifier.
- `calculation_timestamp` (`TIMESTAMP`, NOT NULL): Timestamp metric snapshot was calculated.
- `stock_out_rate` (`NUMERIC(6,2)`, NOT NULL): Percentage of SKUs with zero physical stock.
- `on_time_delivery_pct` (`NUMERIC(6,2)`, NOT NULL): Percentage of inbound shipments delivered on or before SLA date.
- `avg_supplier_lead_time` (`NUMERIC(6,2)`, NOT NULL): Mean delivery cycle duration in days across all suppliers.
- `avg_days_of_inventory` (`NUMERIC(6,2)`, NOT NULL): Portfolio average Days of Inventory Remaining (runway).
- `total_products_monitored` (`INT`, NOT NULL): Active SKUs tracked (100).
- `out_of_stock_products` (`INT`, NOT NULL): Count of SKUs currently depleted.
- `delayed_shipments_count` (`INT`, NOT NULL): Active shipments exceeding SLA delivery dates.
- `created_at` (`TIMESTAMP`, DEFAULT `CURRENT_TIMESTAMP`): Ingest timestamp.

### 2.7 `product_kpis`
SKU-level operational velocity and inventory runway metrics.
- `product_id` (`VARCHAR(20)`, PK, FK): Reference to `products(product_id)`.
- `product_name` (`VARCHAR(150)`): Product name.
- `category` (`VARCHAR(50)`): Product category.
- `current_stock` (`INT`, NOT NULL): Real-time on-hand inventory.
- `avg_daily_demand_30d` (`NUMERIC(10,2)`, NOT NULL): Trailing 30-day mean daily sales velocity.
- `days_of_inventory_remaining` (`NUMERIC(10,2)`, NOT NULL): Current stock divided by average daily consumption rate.
- `is_stock_out` (`BOOLEAN`, DEFAULT `FALSE`): True when `current_stock == 0`.
- `reorder_recommended` (`BOOLEAN`, DEFAULT `FALSE`): True when `current_stock <= reorder_point`.
- `calculated_at` (`TIMESTAMP`, DEFAULT `CURRENT_TIMESTAMP`): Timestamp of calculation.

### 2.8 `anomalies`
Statistical exceptions flagged by the Z-Score detection engine ($|Z| \ge 2.0$).
- `anomaly_id` (`SERIAL`, PK): Sequential anomaly identifier.
- `anomaly_type` (`VARCHAR(30)`, NOT NULL): Type classification (`DEMAND_SPIKE` or `SHIPMENT_DELAY`).
- `reference_id` (`VARCHAR(50)`, NOT NULL): Associated `order_id` or `shipment_id`.
- `entity_name` (`VARCHAR(150)`, NOT NULL): Product name or supplier identifier.
- `metric_value` (`NUMERIC(10,2)`, NOT NULL): Observed value triggering anomaly.
- `baseline_mean` (`NUMERIC(10,2)`, NOT NULL): Historical baseline mean ($\mu$).
- `baseline_std` (`NUMERIC(10,2)`, NOT NULL): Historical standard deviation ($\sigma$).
- `z_score` (`NUMERIC(6,2)`, NOT NULL): Standardized distance from baseline ($Z = \frac{x - \mu}{\sigma}$).
- `severity` (`VARCHAR(20)`, NOT NULL): Severity tier (`HIGH` for $|Z| \ge 2.0$, `CRITICAL` for $|Z| \ge 3.0$).
- `details` (`TEXT`): Human-readable operational context.
- `detected_at` (`TIMESTAMP`, DEFAULT `CURRENT_TIMESTAMP`): Detection timestamp.
- `status` (`VARCHAR(20)`, DEFAULT `'OPEN'`): Resolution status (`OPEN`, `ACKNOWLEDGED`, `RESOLVED`).

### 2.9 `demand_forecasts`
Facebook Prophet 7-day predictive projections per product.
- `forecast_id` (`SERIAL`, PK): Unique forecast entry identifier.
- `product_id` (`VARCHAR(20)`, FK): Reference to `products(product_id)`.
- `forecast_date` (`DATE`, NOT NULL): Future calendar date ($t+1 \dots t+7$).
- `predicted_demand` (`NUMERIC(10,2)`, NOT NULL): Model point estimate $\hat{y}$.
- `confidence_lower` (`NUMERIC(10,2)`, NOT NULL): 90% confidence interval lower bound.
- `confidence_upper` (`NUMERIC(10,2)`, NOT NULL): 90% confidence interval upper bound.
- `current_stock` (`INT`, NOT NULL): Starting on-hand inventory when model was evaluated.
- `projected_stock_remaining` (`NUMERIC(10,2)`, NOT NULL): Expected remaining inventory after meeting cumulative predicted sales.
- `stockout_risk` (`BOOLEAN`, DEFAULT `FALSE`): Flagged `TRUE` if `projected_stock_remaining <= 0`.
- `model_name` (`VARCHAR(50)`, DEFAULT `'Prophet-v1.5'`): Model architecture version identifier.
- `created_at` (`TIMESTAMP`, DEFAULT `CURRENT_TIMESTAMP`): Forecast generation timestamp.
- *Constraint*: `UNIQUE (product_id, forecast_date)` prevents duplicate day forecasts.

### 2.10 `what_if_scenarios`
Simulation records modeling the impact of a +7-day supplier fulfillment delay.
- `scenario_id` (`SERIAL`, PK): Unique simulation entry identifier.
- `scenario_name` (`VARCHAR(50)`, NOT NULL): Scenario name (e.g., `'7_DAY_SUPPLIER_DELAY'`).
- `product_id` (`VARCHAR(20)`, FK): Product evaluated.
- `supplier_id` (`VARCHAR(20)`, FK): Supplier fulfilling the product.
- `product_name` (`VARCHAR(150)`): Product name.
- `category` (`VARCHAR(50)`): Product category.
- `original_lead_time_days` (`INT`, NOT NULL): Nominal baseline replenishment lead time.
- `simulated_lead_time_days` (`INT`, NOT NULL): Extended delay duration (`original_lead_time + 7`).
- `current_inventory` (`INT`, NOT NULL): Starting warehouse inventory buffer.
- `expected_demand_during_delay` (`NUMERIC(10,2)`, NOT NULL): Expected consumer consumption during extended lead time window.
- `projected_stockout_risk` (`BOOLEAN`, DEFAULT `FALSE`): True if demand during delay exceeds current inventory.
- `estimated_units_shortage` (`INT`, DEFAULT `0`): Unmet consumer demand units.
- `impact_severity` (`VARCHAR(20)`, NOT NULL): Impact classification (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `NONE`).
- `analyzed_at` (`TIMESTAMP`, DEFAULT `CURRENT_TIMESTAMP`): Simulation execution timestamp.

### 2.11 `alert_logs`
Operational notification audit ledger.
- `alert_id` (`SERIAL`, PK): Unique alert sequence identifier.
- `alert_type` (`VARCHAR(30)`, NOT NULL): Classification (`CRITICAL_STOCK`, `SHIPMENT_DELAY`).
- `severity` (`VARCHAR(20)`, NOT NULL): Severity level (`WARNING`, `CRITICAL`).
- `title` (`VARCHAR(200)`, NOT NULL): Brief subject header.
- `message` (`TEXT`, NOT NULL): Formatted alert body with affected SKUs/shipments.
- `recipient` (`VARCHAR(100)`): Destination email address or notification channel.
- `delivery_status` (`VARCHAR(20)`, DEFAULT `'LOGGED_ONLY'`): Delivery result (`SENT`, `LOGGED_ONLY`, `FAILED`).
- `created_at` (`TIMESTAMP`, DEFAULT `CURRENT_TIMESTAMP`): Notification dispatch timestamp.

---

## 3. Analytical Views Specification

The Control Tower exposes 6 pre-compiled SQL views designed for low-latency BI querying in Apache Superset and the built-in executive dashboard:

### 3.1 `v_kpi_summary`
Returns a 1-row summary of the latest top-line supply chain health metrics.
```sql
SELECT * FROM v_kpi_summary;
```
Columns: `calculation_timestamp`, `total_products_monitored`, `stock_out_rate`, `on_time_delivery_pct`, `avg_supplier_lead_time`, `avg_days_of_inventory`, `out_of_stock_products`, `delayed_shipments_count`, `total_inventory_units`.

### 3.2 `v_inventory_status`
Enriched real-time view combining product, supplier, and inventory health status.
```sql
SELECT * FROM v_inventory_status WHERE stock_health_status = 'Out of Stock';
```
Columns: `product_id`, `product_name`, `category`, `supplier_name`, `current_stock`, `reorder_point`, `safety_stock`, `stock_status`, `days_of_inventory_remaining`, `avg_daily_demand_30d`, `stock_health_status`, `last_updated`.

### 3.3 `v_shipment_performance`
Supplier fulfillment analytics comparing expected delivery dates against actual receiving timestamps.
```sql
SELECT supplier_name, COUNT(*) AS total_shipments, AVG(delay_days) AS avg_delay
FROM v_shipment_performance
GROUP BY supplier_name;
```
Columns: `shipment_id`, `order_date`, `expected_delivery_date`, `actual_delivery_date`, `shipping_status`, `is_delayed`, `delay_days`, `lead_time_days`, `quantity_shipped`, `supplier_id`, `supplier_name`, `reliability_score`, `product_id`, `product_name`, `category`.

### 3.4 `v_demand_forecast_summary`
Prophet model predictions joined with current warehouse stock levels to highlight imminent stockouts.
```sql
SELECT * FROM v_demand_forecast_summary WHERE stockout_risk = TRUE;
```
Columns: `forecast_id`, `product_id`, `product_name`, `category`, `forecast_date`, `predicted_demand`, `confidence_lower`, `confidence_upper`, `current_stock`, `projected_stock_remaining`, `stockout_risk`, `reorder_point`, `supplier_name`.

### 3.5 `v_anomaly_feed`
Exception log with statistical Z-scores and contextual metadata sorted chronologically.
```sql
SELECT * FROM v_anomaly_feed WHERE severity = 'CRITICAL';
```
Columns: `anomaly_id`, `anomaly_type`, `reference_id`, `entity_name`, `metric_value`, `baseline_mean`, `baseline_std`, `z_score`, `severity`, `details`, `detected_at`, `status`.

### 3.6 `v_what_if_delay_impact`
Simulation impact ledger ordered by largest projected shortage deficit.
```sql
SELECT * FROM v_what_if_delay_impact WHERE impact_severity IN ('CRITICAL', 'HIGH');
```
Columns: `scenario_id`, `scenario_name`, `product_id`, `product_name`, `category`, `supplier_name`, `original_lead_time_days`, `simulated_lead_time_days`, `current_inventory`, `expected_demand_during_delay`, `projected_stockout_risk`, `estimated_units_shortage`, `impact_severity`, `analyzed_at`.

---

## 4. Database Indices & Performance Optimization

To guarantee sub-second dashboard query performance across large order volumes, the following B-Tree indices are active:
- `idx_sales_orders_date_prod` on `sales_orders(order_date, product_id)`
- `idx_shipments_supplier_prod` on `shipments(supplier_id, product_id)`
- `idx_demand_forecasts_date` on `demand_forecasts(forecast_date)`
- `idx_anomalies_type` on `anomalies(anomaly_type, detected_at)`
- `unique_product_forecast_date` on `demand_forecasts(product_id, forecast_date)` (Unique constraint preventing duplicates)
