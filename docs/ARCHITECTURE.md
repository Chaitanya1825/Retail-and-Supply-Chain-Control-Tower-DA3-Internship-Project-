# System Architecture & Technical Design

## 1. Executive Overview

The **Retail & Supply Chain Control Tower** is an enterprise-grade analytics platform that unifies relational transactional data, statistical anomaly detection, Facebook Prophet time-series forecasting, and scenario simulation into an integrated operational command center.

---

## 2. End-to-End System Architecture

```mermaid
flowchart TD
    subgraph Ingestion["1. Ingestion & Synthetic Data Layer"]
        A[Data Generator: generate_data.py] -->|100 Products, 10 Suppliers, 90D Orders, Shipments| B[(PostgreSQL 18 Database)]
    end

    subgraph Storage["2. PostgreSQL Data Platform (11 Tables & 6 Views)"]
        B --> T1[(Core Tables: products, suppliers, inventory, sales_orders, shipments)]
        T1 --> V1[(Analytical Views: v_kpi_summary, v_inventory_status, v_shipment_performance, v_demand_forecast_summary, v_anomaly_feed, v_what_if_delay_impact)]
    end

    subgraph Analytics["3. Analytics & Predictive Modeling Engine"]
        V1 --> K[KPI Calculation: calculate_kpis.py]
        V1 --> Z[Z-Score Anomaly Detection: detect_anomalies.py]
        V1 --> P[Prophet 7-Day Forecasting: forecast_demand.py]
        K & Z & P --> W[What-If Scenario Simulation: what_if_analysis.py]
        W --> AL[Exception Alert Dispatcher: send_alerts.py]
    end

    subgraph Orchestration["4. Pipeline Orchestration"]
        O1[Apache Airflow DAG: @hourly] -.->|Orchestrates| K & Z & P & W & AL
        O2[Native CLI Runner: run_pipeline.py] -.->|Orchestrates| K & Z & P & W & AL
    end

    subgraph Presentation["5. Visualization & Command Interfaces"]
        AL --> D1[Interactive Control Tower Web UI: Streamlit & Plotly]
        AL --> D2[Apache Superset BI: Port 8088]
        AL --> D3[SMTP Email Notifications & Database Audit Logs]
    end
```

---

## 3. Database Entity-Relationship (ER) Architecture

```mermaid
erDiagram
    SUPPLIERS ||--o{ PRODUCTS : supplies
    SUPPLIERS ||--o{ SHIPMENTS : fulfills
    PRODUCTS ||--|| INVENTORY : tracks
    PRODUCTS ||--o{ SALES_ORDERS : generates
    PRODUCTS ||--o{ SHIPMENTS : receives
    PRODUCTS ||--o{ DEMAND_FORECASTS : predicted_by
    PRODUCTS ||--|| PRODUCT_KPIS : aggregates
    PRODUCTS ||--o{ WHAT_IF_SCENARIOS : models

    SUPPLIERS {
        varchar supplier_id PK
        varchar supplier_name
        varchar contact_name
        varchar city
        numeric reliability_score
    }
    PRODUCTS {
        varchar product_id PK
        varchar product_name
        varchar category
        numeric unit_price
        numeric cost_price
        int reorder_point
        int lead_time_days
        varchar supplier_id FK
    }
    INVENTORY {
        int inventory_id PK
        varchar product_id FK
        int current_stock
        int reserved_stock
        int available_stock
        varchar stock_status
    }
    SALES_ORDERS {
        varchar order_id PK
        date order_date
        varchar product_id FK
        int quantity_ordered
        numeric total_amount
    }
    SHIPMENTS {
        varchar shipment_id PK
        varchar supplier_id FK
        varchar product_id FK
        date order_date
        date expected_delivery_date
        date actual_delivery_date
        int delay_days
        int lead_time_days
        boolean is_delayed
        varchar shipping_status
    }
    DEMAND_FORECASTS {
        int forecast_id PK
        varchar product_id FK
        date forecast_date
        numeric predicted_demand
        numeric confidence_lower
        numeric confidence_upper
        numeric projected_stock_remaining
        boolean stockout_risk
    }
```

---

## 4. Pipeline Execution Sequence

```mermaid
sequenceDiagram
    autonumber
    participant Orch as Airflow / run_pipeline.py
    participant DB as PostgreSQL 18
    participant Calc as Analytics Engine
    participant ML as Prophet Forecaster
    participant Alert as Notification Dispatcher
    participant UI as Dashboard

    Orch->>DB: 1. Refresh inventory burn & advance in-transit shipments
    Orch->>Calc: 2. Calculate Stockout %, OTD %, Lead Time & DOI
    Calc->>DB: Persist into kpi_metrics & product_kpis
    Orch->>Calc: 3. Compute Z-Scores on Daily Demand & Transit Delays
    Calc->>DB: Persist detected outliers (|Z| >= 2.0) into anomalies
    Orch->>ML: 4. Fit Prophet models across 100 SKUs (7-day horizon)
    ML->>DB: Persist 700 forecast points & stockout risks into demand_forecasts
    Orch->>Calc: 5. Simulate +7 day supplier delay & compute unit deficits
    Calc->>DB: Persist results into what_if_scenarios
    Orch->>Alert: 6. Evaluate critical conditions (stockouts & extreme delays)
    Alert->>DB: Log dispatch event into alert_logs
    Alert-->>UI: Real-time update via database views
```

---

## 5. Mathematical Formulations

### 5.1 Stock-Out Rate
Measures the percentage of catalog SKUs unable to fulfill customer orders due to zero stock:
$$\text{Stock-Out Rate} = \left( \frac{\sum_{i=1}^{N} \mathbb{I}(\text{Current Stock}_i = 0)}{N} \right) \times 100\%$$
- **Benchmark in Project**: 5 out of 100 products = **5.0%**.

### 5.2 On-Time Delivery Percentage (OTD %)
Evaluates supplier fulfillment reliability:
$$\text{OTD \%} = \left( \frac{\text{Shipments where Actual Delivery Date} \le \text{Expected Delivery Date}}{\text{Total Evaluated Shipments}} \right) \times 100\%$$
- **Benchmark in Project**: 169 on-time out of 207 delivered shipments = **81.6%**.

### 5.3 Days of Inventory Remaining (DOI / Days of Supply)
Computes stock runway based on the trailing 30-day consumption velocity:
$$\text{Avg Daily Demand}_{30d} = \frac{\sum_{t=1}^{30} \text{Daily Quantity Ordered}_t}{30}$$
$$\text{Days of Inventory Remaining} = \frac{\text{Current Stock}}{\max(\text{Avg Daily Demand}_{30d}, 0.2)}$$
- **Benchmark in Project**: Portfolio average = **87.5 days**.

### 5.4 Statistical Z-Score Anomaly Detection
Standardizes deviations from baseline distributions to isolate operational outliers:
$$Z = \frac{x - \mu}{\sigma}$$
- **Thresholds**:
  - $|Z| \ge 2.0$: High Severity Alert
  - $|Z| \ge 3.0$: Critical Severity Alert

### 5.5 Facebook Prophet Time-Series Demand Forecasting
Decomposes daily demand into piecewise linear trend, weekly seasonality, and Gaussian error:
$$y(t) = g(t) + s(t) + \epsilon_t, \quad \epsilon_t \sim \mathcal{N}(0, \sigma^2)$$
Stockout risk is triggered when cumulative forecasted demand exceeds on-hand stock:
$$\text{Stockout Risk} = \text{True} \iff \text{Current Stock} - \sum_{k=1}^{7} \hat{y}(t+k) \le 0$$

### 5.6 What-If 7-Day Supplier Delay Simulation
Models the operational deficit created when replenishment shipments are delayed by 7 days:
$$\text{Simulated Lead Time} = \text{Nominal Lead Time} + 7$$
$$\text{Projected Balance} = \text{Current Stock} - (\text{Simulated Lead Time} \times \text{Avg Daily Demand})$$
$$\text{Shortage Units} = \max(0, -\text{Projected Balance})$$
