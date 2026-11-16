# Control Tower Dashboard Screenshots Guide

This directory holds presentation-quality screenshots of the **Retail & Supply Chain Control Tower** dashboard for project submission, portfolio demonstration, and client presentations.

---

## Required Dashboard Views to Capture

When running the dashboard (`streamlit run run_dashboard.py` at `http://localhost:8501`), capture the following 6 core analytical views:

| Filename | Dashboard View / Tab | Key Features to Highlight in Screenshot |
|---|---|---|
| `01_overview_dashboard.png` | **Overview** | Top KPI cards (Total SKUs, Inventory Units, Stockout %, OTD %, Lead Time), 90-day demand velocity area curve, stock health ratio donut chart, and live US logistics map. |
| `02_inventory_monitor.png` | **Inventory** | Stock health status metrics (Healthy, Low Stock, Stockouts), search and category filtering toolbar, and the product inventory ledger with reorder points. |
| `03_shipment_logistics.png` | **Shipments** | Carrier performance metrics, lead time histogram distribution, delayed shipments ranking by vendor, and tracking status pills (`Delivered`, `In Transit`, `Delayed`). |
| `04_demand_forecasting.png` | **Demand Forecast** | Interactive SKU forecast curve displaying 30-day historical actual demand, 7-day Prophet predicted demand, 90% confidence envelope, and stock depletion runway. |
| `05_anomaly_detection.png` | **Anomalies** | Z-Score outlier scatter matrix ($|Z| \ge 2.0$), severity color-coding (`CRITICAL` vs `HIGH`), and the live exception event stream table. |
| `06_what_if_simulation.png` | **What-If Analysis** | Interactive +7 day supplier delay slider, projected stockout count, unit shortage bar chart, and scenario vulnerability matrix. |

---

## Instructions for Capturing High-Resolution Screenshots on Windows

1. **Launch the Dashboard**:
   ```powershell
   streamlit run run_dashboard.py
   ```
2. **Maximize Browser Window**:
   - Open browser at `http://localhost:8501`.
   - Set zoom level to `100%` (or press `Ctrl + 0`).
   - Use Full Screen (`F11`) for maximum viewable canvas.
3. **Capture Crisp Screenshot**:
   - Press **`Windows Key + Shift + S`** (Windows Snipping Tool).
   - Select the entire application viewport.
   - Save the image as a `.png` file in this directory (`docs/screenshots/`).
4. **Recommended Specifications**:
   - Format: `PNG` (lossless for sharp typography and charts).
   - Recommended Resolution: `1920 × 1080` (1080p Full HD) or higher.

