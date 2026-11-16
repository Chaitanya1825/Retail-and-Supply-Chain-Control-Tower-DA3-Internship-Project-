"""
Data Refresh Engine for Retail & Supply Chain Control Tower.
Called by the hourly Airflow DAG to:
1. Refresh inventory levels (simulates hourly stock burn and replenishment receipts)
2. Update shipment statuses (advances in-transit shipments, checks arrivals)
3. Persists updated states into PostgreSQL
"""
import sys
import random
from datetime import datetime, timedelta, date
from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config.settings import get_engine

def refresh_inventory_and_shipments():
    """Refreshes inventory and shipment records for the hourly cycle."""
    engine = get_engine()
    print("=" * 60)
    print("  HOURLY DATA REFRESH: INVENTORY & SHIPMENTS")
    print("=" * 60)
    
    with engine.begin() as conn:
        # 1. Update In-Transit shipments that have reached or passed their delivery dates
        print("[*] Checking and updating in-transit shipments...")
        conn.exec_driver_sql("""
            UPDATE shipments
            SET 
                shipping_status = CASE 
                    WHEN actual_delivery_date IS NOT NULL AND actual_delivery_date > expected_delivery_date THEN 'DELAYED'
                    ELSE 'DELIVERED'
                END,
                actual_delivery_date = COALESCE(actual_delivery_date, CURRENT_DATE)
            WHERE shipping_status = 'IN_TRANSIT' AND expected_delivery_date <= CURRENT_DATE;
        """)
        
        # 2. Simulate recent hourly retail sales deductions on 5-10 active products
        print("[*] Processing recent sales consumption...")
        df_active = pd.read_sql("SELECT product_id, current_stock, reorder_point FROM inventory WHERE current_stock > 5", conn)
        if not df_active.empty:
            sample_prods = df_active.sample(n=min(8, len(df_active)))
            for _, r in sample_prods.iterrows():
                deduction = random.randint(1, 4)
                conn.exec_driver_sql(
                    "UPDATE inventory SET current_stock = GREATEST(0, current_stock - %s), last_updated = CURRENT_TIMESTAMP WHERE product_id = %s",
                    (deduction, r["product_id"])
                )
                
        # 3. Synchronize stock status classifications
        print("[*] Re-evaluating stock status flags ('IN_STOCK', 'LOW_STOCK', 'OUT_OF_STOCK')...")
        conn.exec_driver_sql("""
            UPDATE inventory
            SET stock_status = CASE 
                WHEN current_stock = 0 THEN 'OUT_OF_STOCK'
                WHEN current_stock <= reorder_point THEN 'LOW_STOCK'
                ELSE 'IN_STOCK'
            END,
            available_stock = GREATEST(0, current_stock - reserved_stock),
            last_updated = CURRENT_TIMESTAMP;
        """)
        
    print("[✓] Inventory and shipment records successfully refreshed.")
    print("=" * 60)

if __name__ == "__main__":
    refresh_inventory_and_shipments()

