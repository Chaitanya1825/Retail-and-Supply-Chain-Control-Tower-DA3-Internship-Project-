"""
Superset Asset Generator & Documentation Exporter.
Generates:
1. Superset Database connection definitions (PostgreSQL)
2. Superset Dataset metadata for all 6 analytical views
3. Superset Dashboard JSON configuration containing all 10 required cards and charts:
   - Total products
   - Current inventory
   - Stock-out rate
   - On-time delivery percentage
   - Supplier lead time
   - Inventory status
   - Shipment delays
   - Demand forecasts
   - Anomaly alerts
   - Seven-day supplier delay scenario
Saves assets in docs/superset/ for instant 1-click import into Apache Superset.
"""
import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SUPERSET_DOCS_DIR = ROOT_DIR / "docs" / "superset"
SUPERSET_DOCS_DIR.mkdir(parents=True, exist_ok=True)

SUPERSET_DB_CONFIG = {
    "database_name": "Retail Control Tower PostgreSQL",
    "sqlalchemy_uri": "postgresql://postgres:<your_password>@host.docker.internal:5432/supply_chain_control_tower",
    "tables": [
        {
            "table_name": "v_kpi_summary",
            "description": "Executive Top-Line KPI Summary (Stock-Out Rate, OTD%, Lead Time, Inventory)"
        },
        {
            "table_name": "v_inventory_status",
            "description": "Inventory Health, Reorder Levels, and Stock Status Breakdown"
        },
        {
            "table_name": "v_shipment_performance",
            "description": "Shipment Delays, Lead Time by Supplier, and Delivery Reliability"
        },
        {
            "table_name": "v_demand_forecast_summary",
            "description": "Prophet 7-Day Demand Forecasts & Projected Stockout Risks"
        },
        {
            "table_name": "v_anomaly_feed",
            "description": "Statistical Z-Score Anomaly Alerts (Demand Spikes & Shipment Delays)"
        },
        {
            "table_name": "v_what_if_delay_impact",
            "description": "What-If Scenario Simulation: 7-Day Supplier Delivery Delay Impact"
        }
    ]
}

SUPERSET_DASHBOARD_METADATA = {
    "dashboard_title": "Retail and Supply Chain Control Tower",
    "description": "Data Analytics Internship Project - Executive Supply Chain Performance, Forecasting & Risk Monitoring",
    "css": "",
    "charts": [
        {
            "slice_name": "Total Products Monitored",
            "viz_type": "big_number_total",
            "datasource": "v_kpi_summary",
            "metric": "MAX(total_products_monitored)",
            "header": "Total Products"
        },
        {
            "slice_name": "Total Current Inventory Units",
            "viz_type": "big_number_total",
            "datasource": "v_kpi_summary",
            "metric": "MAX(total_inventory_units)",
            "header": "Current Inventory"
        },
        {
            "slice_name": "Stock-Out Rate (%)",
            "viz_type": "big_number_total",
            "datasource": "v_kpi_summary",
            "metric": "MAX(stock_out_rate)",
            "header": "Stock-Out Rate"
        },
        {
            "slice_name": "On-Time Delivery (%)",
            "viz_type": "big_number_total",
            "datasource": "v_kpi_summary",
            "metric": "MAX(on_time_delivery_pct)",
            "header": "On-Time Delivery %"
        },
        {
            "slice_name": "Average Supplier Lead Time (Days)",
            "viz_type": "big_number_total",
            "datasource": "v_kpi_summary",
            "metric": "MAX(avg_supplier_lead_time)",
            "header": "Supplier Lead Time"
        },
        {
            "slice_name": "Inventory Health Breakdown",
            "viz_type": "pie",
            "datasource": "v_inventory_status",
            "groupby": ["stock_health_status"],
            "metric": "COUNT(*)",
            "header": "Inventory Status"
        },
        {
            "slice_name": "Supplier Lead Times & Delayed Deliveries",
            "viz_type": "dist_bar",
            "datasource": "v_shipment_performance",
            "groupby": ["supplier_name"],
            "metric": "AVG(lead_time_days)",
            "header": "Shipment Delays"
        },
        {
            "slice_name": "7-Day Prophet Demand Forecast & Stockout Risk",
            "viz_type": "line",
            "datasource": "v_demand_forecast_summary",
            "time_range": "No filter",
            "metrics": ["AVG(predicted_demand)", "AVG(projected_stock_remaining)"],
            "groupby": ["forecast_date"],
            "header": "Demand Forecasts"
        },
        {
            "slice_name": "Z-Score Anomaly Outlier Alerts",
            "viz_type": "table",
            "datasource": "v_anomaly_feed",
            "columns": ["anomaly_type", "entity_name", "metric_value", "baseline_mean", "z_score", "severity", "detected_at"],
            "header": "Anomaly Alerts"
        },
        {
            "slice_name": "Seven-Day Supplier Delay Scenario Impact",
            "viz_type": "bar",
            "datasource": "v_what_if_delay_impact",
            "groupby": ["product_name"],
            "metric": "SUM(estimated_units_shortage)",
            "header": "Seven-Day Supplier Delay Scenario"
        }
    ]
}

def export_superset_configs():
    """Writes Superset import JSON files and guides into docs/superset/."""
    print("[*] Generating Superset Dashboard configuration files...")
    
    db_file = SUPERSET_DOCS_DIR / "superset_database_connection.json"
    with open(db_file, "w", encoding="utf-8") as f:
        json.dump(SUPERSET_DB_CONFIG, f, indent=2)
        
    dash_file = SUPERSET_DOCS_DIR / "control_tower_dashboard_export.json"
    with open(dash_file, "w", encoding="utf-8") as f:
        json.dump(SUPERSET_DASHBOARD_METADATA, f, indent=2)
        
    guide_file = SUPERSET_DOCS_DIR / "SUPERSET_SETUP_GUIDE.md"
    guide_content = """# Apache Superset Setup Guide for Retail Control Tower

This guide provides instructions to connect Apache Superset to the PostgreSQL database and load the Control Tower Dashboard.

## 1. Database Connection in Superset
1. Log in to Superset (default `http://localhost:8088`, credentials `admin`/`admin`).
2. Go to **Settings > Database Connections > + Database**.
3. Select **PostgreSQL**.
4. Enter the connection parameters:
   - **Host**: `localhost` (or `host.docker.internal` if Superset is running inside Docker)
   - **Port**: `5432`
   - **Database Name**: `supply_chain_control_tower`
   - **Username**: `postgres`
   - **Password**: `<your_database_password>`
   - **SQLAlchemy URI**: `postgresql://postgres:<your_password>@localhost:5432/supply_chain_control_tower`
5. Click **Test Connection** then **Connect**.

## 2. Register Analytical Datasets (Views)
Go to **Datasets > + Dataset** and add the following views from schema `public`:
1. `v_kpi_summary`
2. `v_inventory_status`
3. `v_shipment_performance`
4. `v_demand_forecast_summary`
5. `v_anomaly_feed`
6. `v_what_if_delay_impact`

## 3. The 10 Dashboard Charts
The dashboard contains:
1. **Total Products** (Big Number: `v_kpi_summary.total_products_monitored`)
2. **Current Inventory** (Big Number: `v_kpi_summary.total_inventory_units`)
3. **Stock-out Rate** (Big Number: `v_kpi_summary.stock_out_rate`)
4. **On-Time Delivery %** (Big Number: `v_kpi_summary.on_time_delivery_pct`)
5. **Supplier Lead Time** (Big Number: `v_kpi_summary.avg_supplier_lead_time`)
6. **Inventory Status** (Pie Chart: `v_inventory_status.stock_health_status`)
7. **Shipment Delays** (Bar Chart: `v_shipment_performance.lead_time_days` by `supplier_name`)
8. **Demand Forecasts** (Line Chart: `v_demand_forecast_summary.predicted_demand` vs `projected_stock_remaining`)
9. **Anomaly Alerts** (Table / Scatter Chart: `v_anomaly_feed` Z-scores)
10. **Seven-Day Supplier Delay Scenario** (Bar Chart: `v_what_if_delay_impact.estimated_units_shortage`)

You can also view all 10 cards interactively with the built-in Control Tower Web UI:
```powershell
streamlit run run_dashboard.py
```
"""
    with open(guide_file, "w", encoding="utf-8") as f:
        f.write(guide_content)
        
    print(f"[✓] Superset configuration assets exported to {SUPERSET_DOCS_DIR}")

if __name__ == "__main__":
    export_superset_configs()

