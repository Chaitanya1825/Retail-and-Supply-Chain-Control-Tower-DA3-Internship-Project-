"""
KPI Calculation Engine for Retail & Supply Chain Control Tower.
Calculates:
1. Stock-out Rate (%)
2. On-Time Delivery Percentage (%)
3. Average Supplier Lead Time (Days)
4. Days of Inventory Remaining (Product-level & Portfolio Average)
Persists metrics into PostgreSQL (kpi_metrics & product_kpis).
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config.settings import get_engine

def calculate_and_store_kpis():
    """Computes all supply chain KPIs and stores snapshots in PostgreSQL."""
    engine = get_engine()
    print("=" * 60)
    print("  CALCULATING SUPPLY CHAIN CONTROL TOWER KPIS")
    print("=" * 60)
    
    with engine.connect() as conn:
        # Load tables into DataFrames
        df_inventory = pd.read_sql("SELECT * FROM inventory", conn)
        df_products = pd.read_sql("SELECT * FROM products", conn)
        df_shipments = pd.read_sql("SELECT * FROM shipments", conn)
        
        # Pull last 30 days sales for burn-rate / days of inventory
        thirty_days_ago = (datetime.now() - timedelta(days=30)).date()
        df_sales_30d = pd.read_sql(
            f"SELECT product_id, quantity_ordered FROM sales_orders WHERE order_date >= '{thirty_days_ago}'", 
            conn
        )
        
    total_products = len(df_products)
    if total_products == 0:
        print("[!] No products found in database.")
        return
        
    # 1. Stock-Out Rate
    # Count products where current_stock == 0
    # Avoid duplicate column collisions like reorder_point
    inv_cols = ["product_id", "current_stock", "reserved_stock", "available_stock", "stock_status"]
    merged_inv = pd.merge(df_products, df_inventory[inv_cols], on="product_id", how="left")
    merged_inv["current_stock"] = merged_inv["current_stock"].fillna(0).astype(int)
    out_of_stock_count = int((merged_inv["current_stock"] == 0).sum())
    stock_out_rate = round((out_of_stock_count / total_products) * 100.0, 2)
    print(f"[*] Total Monitored Products: {total_products}")
    print(f"[*] Out of Stock Products: {out_of_stock_count}")
    print(f"[✓] Stock-Out Rate: {stock_out_rate}%")
    
    # 2. On-Time Delivery Percentage (OTD %)
    # Consider delivered shipments or shipments with evaluated delivery
    evaluated_shipments = df_shipments[df_shipments["shipping_status"].isin(["DELIVERED", "DELAYED"])].copy()
    if len(evaluated_shipments) > 0:
        on_time_count = int((evaluated_shipments["is_delayed"] == False).sum())
        delayed_count = int((evaluated_shipments["is_delayed"] == True).sum())
        on_time_delivery_pct = round((on_time_count / len(evaluated_shipments)) * 100.0, 2)
    else:
        delayed_count = 0
        on_time_delivery_pct = 100.0
    print(f"[*] Evaluated Shipments: {len(evaluated_shipments)} (Delayed: {delayed_count})")
    print(f"[✓] On-Time Delivery Percentage: {on_time_delivery_pct}%")
    
    # 3. Average Supplier Lead Time
    # Using actual or nominal lead_time_days
    if "lead_time_days" in df_shipments.columns and not df_shipments["lead_time_days"].dropna().empty:
        avg_supplier_lead_time = round(float(df_shipments["lead_time_days"].dropna().mean()), 2)
    else:
        avg_supplier_lead_time = round(float(df_products["lead_time_days"].mean()), 2)
    print(f"[✓] Average Supplier Lead Time: {avg_supplier_lead_time} days")
    
    # 4. Days of Inventory Remaining (DOI) per product & Portfolio Avg
    # Daily demand = (total qty sold last 30 days) / 30
    sales_grouped = df_sales_30d.groupby("product_id")["quantity_ordered"].sum().reset_index()
    sales_grouped.rename(columns={"quantity_ordered": "total_sold_30d"}, inplace=True)
    
    prod_metrics = pd.merge(merged_inv, sales_grouped, on="product_id", how="left")
    prod_metrics["total_sold_30d"] = prod_metrics["total_sold_30d"].fillna(0)
    prod_metrics["avg_daily_demand_30d"] = prod_metrics["total_sold_30d"] / 30.0
    # Avoid zero division: minimum baseline demand 0.2 units/day
    prod_metrics["effective_daily_demand"] = prod_metrics["avg_daily_demand_30d"].apply(lambda x: max(x, 0.2))
    prod_metrics["days_of_inventory_remaining"] = (
        prod_metrics["current_stock"] / prod_metrics["effective_daily_demand"]
    ).round(2)
    
    prod_metrics["is_stock_out"] = prod_metrics["current_stock"] == 0
    prod_metrics["reorder_recommended"] = (
        (prod_metrics["current_stock"] <= prod_metrics["reorder_point"]) | (prod_metrics["days_of_inventory_remaining"] <= prod_metrics["lead_time_days"])
    )
    
    avg_days_of_inventory = round(float(prod_metrics["days_of_inventory_remaining"].mean()), 2)
    print(f"[✓] Portfolio Average Days of Inventory: {avg_days_of_inventory} days")
    
    # Prepare Product-level KPIs table
    product_kpi_records = []
    for _, row in prod_metrics.iterrows():
        product_kpi_records.append({
            "product_id": row["product_id"],
            "product_name": row["product_name"],
            "category": row["category"],
            "current_stock": int(row["current_stock"]),
            "avg_daily_demand_30d": round(float(row["avg_daily_demand_30d"]), 2),
            "days_of_inventory_remaining": round(float(row["days_of_inventory_remaining"]), 2),
            "is_stock_out": bool(row["is_stock_out"]),
            "reorder_recommended": bool(row["reorder_recommended"]),
            "calculated_at": datetime.now()
        })
    df_product_kpi_to_save = pd.DataFrame(product_kpi_records)
    
    # Overall summary metric record
    summary_metric = {
        "calculation_timestamp": datetime.now(),
        "stock_out_rate": stock_out_rate,
        "on_time_delivery_pct": on_time_delivery_pct,
        "avg_supplier_lead_time": avg_supplier_lead_time,
        "avg_days_of_inventory": avg_days_of_inventory,
        "total_products_monitored": total_products,
        "out_of_stock_products": out_of_stock_count,
        "delayed_shipments_count": delayed_count,
        "created_at": datetime.now()
    }
    df_summary_to_save = pd.DataFrame([summary_metric])
    
    # Store into PostgreSQL
    print("[*] Persisting KPI results to PostgreSQL...")
    with engine.begin() as conn:
        # Save historical KPI snapshot
        df_summary_to_save.to_sql("kpi_metrics", conn, if_exists="append", index=False)
        
        # Refresh product-level KPIs
        conn.exec_driver_sql("TRUNCATE TABLE product_kpis CASCADE;")
        df_product_kpi_to_save.to_sql("product_kpis", conn, if_exists="append", index=False)
        
    print("[✓] All KPIs successfully stored in database.")
    print("=" * 60)
    return summary_metric

if __name__ == "__main__":
    calculate_and_store_kpis()
