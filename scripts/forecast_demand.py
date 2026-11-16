"""
Demand Forecasting Module for Retail & Supply Chain Control Tower.
Uses Facebook Prophet to forecast demand for each product for the next 7 days.
Compares forecasted demand with current inventory to identify products at risk of stock-outs.
Stores forecasts and stockout risk evaluations in PostgreSQL.
"""
import sys
import logging
from datetime import datetime, timedelta, date
from pathlib import Path
import pandas as pd
import numpy as np
from prophet import Prophet

# Suppress noisy logs from cmdstanpy & prophet
logging.getLogger("prophet").setLevel(logging.ERROR)
logging.getLogger("cmdstanpy").setLevel(logging.ERROR)

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config.settings import get_engine, PROPHET_FORECAST_HORIZON_DAYS

def generate_demand_forecasts(horizon_days: int = PROPHET_FORECAST_HORIZON_DAYS):
    """Forecasts daily demand for each product using Facebook Prophet and detects stockout risk."""
    engine = get_engine()
    print("=" * 60)
    print(f"  RUNNING PROPHET DEMAND FORECASTING ({horizon_days}-DAY HORIZON)")
    print("=" * 60)
    
    with engine.connect() as conn:
        df_sales = pd.read_sql("SELECT order_date, product_id, quantity_ordered FROM sales_orders", conn)
        df_inventory = pd.read_sql("SELECT product_id, current_stock, reorder_point FROM inventory", conn)
        df_products = pd.read_sql("SELECT product_id, product_name, category FROM products", conn)
        
    inv_lookup = dict(zip(df_inventory["product_id"], df_inventory["current_stock"]))
    prod_name_lookup = dict(zip(df_products["product_id"], df_products["product_name"]))
    
    # Aggregate daily demand per product
    daily_sales = df_sales.groupby(["product_id", "order_date"])["quantity_ordered"].sum().reset_index()
    daily_sales["order_date"] = pd.to_datetime(daily_sales["order_date"])
    
    all_forecast_records = []
    at_risk_products = set()
    
    unique_products = df_products["product_id"].unique()
    total_prods = len(unique_products)
    print(f"[*] Forecasting demand for {total_prods} products over the next {horizon_days} days...")
    
    # Ensure continuous date index across the last 90 days for accurate Prophet fitting
    min_date = daily_sales["order_date"].min()
    max_date = daily_sales["order_date"].max()
    full_date_range = pd.date_range(start=min_date, end=max_date, freq="D")
    
    start_time = datetime.now()
    
    for idx, p_id in enumerate(unique_products, start=1):
        p_sales = daily_sales[daily_sales["product_id"] == p_id][["order_date", "quantity_ordered"]].copy()
        
        # Reindex with 0 for days without sales to provide full continuous time series
        p_sales = p_sales.set_index("order_date").reindex(full_date_range, fill_value=0).reset_index()
        p_sales.columns = ["ds", "y"]
        p_sales["y"] = p_sales["y"].astype(float)
        
        curr_stock = int(inv_lookup.get(p_id, 0))
        
        try:
            # Fit Prophet with weekly seasonality
            model = Prophet(
                growth="linear",
                weekly_seasonality=True,
                yearly_seasonality=False,
                daily_seasonality=False,
                interval_width=0.90
            )
            model.fit(p_sales)
            
            # Predict future horizon
            future_df = model.make_future_dataframe(periods=horizon_days, freq="D", include_history=False)
            pred = model.predict(future_df)
            
            cumulative_demand = 0.0
            
            for _, row in pred.iterrows():
                f_date = row["ds"].date()
                yhat = max(0.0, float(row["yhat"]))
                yhat_lower = max(0.0, float(row["yhat_lower"]))
                yhat_upper = max(0.0, float(row["yhat_upper"]))
                
                cumulative_demand += yhat
                projected_remaining = curr_stock - cumulative_demand
                
                # Flag stockout risk if cumulative demand exceeds current stock
                has_stockout_risk = (curr_stock == 0) or (projected_remaining <= 0)
                if has_stockout_risk:
                    at_risk_products.add(p_id)
                    
                all_forecast_records.append({
                    "product_id": p_id,
                    "forecast_date": f_date,
                    "predicted_demand": round(yhat, 2),
                    "confidence_lower": round(yhat_lower, 2),
                    "confidence_upper": round(yhat_upper, 2),
                    "current_stock": curr_stock,
                    "projected_stock_remaining": round(projected_remaining, 2),
                    "stockout_risk": bool(has_stockout_risk),
                    "model_name": "Prophet-v1.5",
                    "created_at": datetime.now()
                })
        except Exception as e:
            # Fallback simple moving average forecast if Prophet hits singular matrix
            print(f"[!] Warning: Prophet fallback for {p_id}: {e}")
            baseline_demand = float(p_sales["y"].tail(14).mean())
            cumulative_demand = 0.0
            for day_offset in range(1, horizon_days + 1):
                f_date = (max_date + timedelta(days=day_offset)).date()
                cumulative_demand += baseline_demand
                rem = curr_stock - cumulative_demand
                risk = (curr_stock == 0) or (rem <= 0)
                if risk:
                    at_risk_products.add(p_id)
                all_forecast_records.append({
                    "product_id": p_id,
                    "forecast_date": f_date,
                    "predicted_demand": round(baseline_demand, 2),
                    "confidence_lower": round(max(0.0, baseline_demand * 0.7), 2),
                    "confidence_upper": round(baseline_demand * 1.3, 2),
                    "current_stock": curr_stock,
                    "projected_stock_remaining": round(rem, 2),
                    "stockout_risk": bool(risk),
                    "model_name": "MovingAverage-Fallback",
                    "created_at": datetime.now()
                })
                
        if idx % 20 == 0 or idx == total_prods:
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"    -> Processed {idx}/{total_prods} products ({elapsed:.1f}s)")
            
    df_forecasts = pd.DataFrame(all_forecast_records)
    
    print(f"[✓] Generated {len(df_forecasts)} daily forecast points.")
    print(f"[!] Products identified at risk of stock-out within {horizon_days} days: {len(at_risk_products)} products")
    for p_id in sorted(list(at_risk_products))[:7]:
        print(f"      - {p_id}: {prod_name_lookup.get(p_id)} (Current stock: {inv_lookup.get(p_id)})")
    if len(at_risk_products) > 7:
        print(f"      ... and {len(at_risk_products) - 7} more.")
        
    print("[*] Persisting forecast results to PostgreSQL...")
    with engine.begin() as conn:
        conn.exec_driver_sql("TRUNCATE TABLE demand_forecasts CASCADE;")
        df_forecasts.to_sql("demand_forecasts", conn, if_exists="append", index=False)
        
    print("[✓] Demand forecasts and stockout risks saved successfully.")
    print("=" * 60)
    return df_forecasts

if __name__ == "__main__":
    generate_demand_forecasts()

