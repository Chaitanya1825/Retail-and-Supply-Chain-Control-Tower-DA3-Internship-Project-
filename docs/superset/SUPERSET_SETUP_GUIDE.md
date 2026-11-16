# Apache Superset Setup Guide for Retail Control Tower

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
