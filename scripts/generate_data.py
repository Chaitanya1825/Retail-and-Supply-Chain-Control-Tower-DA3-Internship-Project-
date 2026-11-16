"""
Synthetic Data Generator & Loader for Retail & Supply Chain Control Tower.
Generates:
- 10 Suppliers
- 100 Products across 6 categories
- Current Inventory for 100 products (with realistic stockout/low-stock distributions)
- Daily Sales Orders for the last 90 days (with seasonality and demand spikes)
- Shipments & Delivery records (with on-time and delayed shipments)
Saves CSV snapshots in data/ and loads directly into PostgreSQL.
"""
import sys
import random
from datetime import datetime, timedelta, date
from pathlib import Path
import pandas as pd
import numpy as np

# Ensure root dir is in python path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config.settings import get_engine, BASE_DIR

# Set random seed for reproducible yet realistic data
np.random.seed(42)
random.seed(42)

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CATEGORIES = {
    "Electronics": ["Wireless Earbuds", "Smartwatch Pro", "Noise-Cancelling Headphones", "Bluetooth Speaker", "HD Webcam", "Fast Charger 65W", "USB-C Hub Multiport", "Gaming Mouse", "Mechanical Keyboard", "Portable Power Bank"],
    "Apparel": ["Classic Cotton T-Shirt", "Slim Fit Denim Jeans", "Fleece Zip Hoodie", "Waterproof Rain Jacket", "Thermal Base Layer", "Athletic Crew Socks 3-Pack", "Canvas Walking Shoes", "Wool Blend Beanie", "Running Shorts", "Breathable Polo Shirt"],
    "Home & Kitchen": ["Stainless Steel Chef Knife", "Cast Iron Skillet 10in", "Digital Kitchen Scale", "Ceramic Pour-Over Dripper", "Double-Wall Insulated Tumbler", "Silicone Utensil Set", "Non-Stick Baking Sheet", "Electric Spice Grinder", "Aroma Oil Diffuser", "Organic Bamboo Cutting Board"],
    "Health & Personal Care": ["Sonic Electric Toothbrush", "Immune Defense Multi-Vitamin", "Hydrating Facial Cleanser", "Mineral Sunscreen SPF 50", "Massage Gun Deep Tissue", "Collagen Peptide Powder", "Natural Deodorant Stick", "Lavender Bath Salts", "Moisturizing Hand Cream", "Adjustable Sleep Mask"],
    "Sports & Outdoors": ["Anti-Burst Yoga Mat", "Stainless Steel Water Bottle 32oz", "Resistance Bands Loop Set", "Camping Hammock with Straps", "Trekking Poles Carbon Fiber", "Compact Bike Pump", "Trail Running Hydration Vest", "Polarized Sunglasses", "Gym Duffel Bag Waterproof", "Quick-Dry Microfiber Towel"],
    "Toys & Games": ["Strategy Board Game", "Building Bricks Architecture Set", "Remote Control Racing Buggy", "Speed Cube Puzzle 3x3", "STEM Solar Robot Kit", "Classic Wood Chess Set", "Magnetic Tiles 60-Piece", "Flying Drone with Camera", "Card Game Party Pack", "Artistic Watercolor Studio"]
}

SUPPLIER_NAMES = [
    ("Apex Global Logistics", "Alice Johnson", "alice@apexlogistics.com", "555-0101", "Chicago", 94.5),
    ("Prime Source Supply", "Bob Smith", "bsmith@primesource.com", "555-0102", "Dallas", 96.0),
    ("Horizon Electronics Mfg", "Carol Danvers", "carol@horizonmfg.com", "555-0103", "San Jose", 91.2),
    ("BlueWave Distribution", "David Miller", "dmiller@bluewave.com", "555-0104", "Seattle", 88.5),
    ("Vertex Goods & Materials", "Elena Rostova", "elena@vertexgoods.com", "555-0105", "Atlanta", 97.5),
    ("Pinnacle Packaging & Parts", "Frank Castle", "frank@pinnacle.com", "555-0106", "Denver", 89.0),
    ("Beacon Industrial Corp", "Grace Hopper", "grace@beaconind.com", "555-0107", "Boston", 93.8),
    ("Nexus Materials Direct", "Henry Zhang", "henry@nexusdirect.com", "555-0108", "New York", 95.2),
    ("Pacific Freight & Imports", "Isabel Morales", "isabel@pacificfreight.com", "555-0109", "Los Angeles", 84.0),
    ("Summit Retail Solutions", "Jack Ryan", "jack@summitretail.com", "555-0110", "Columbus", 92.0)
]

def generate_suppliers() -> pd.DataFrame:
    """Generates 10 suppliers."""
    suppliers_data = []
    for idx, (name, contact, email, phone, city, rel) in enumerate(SUPPLIER_NAMES, start=1):
        s_id = f"SUP-{idx:03d}"
        suppliers_data.append({
            "supplier_id": s_id,
            "supplier_name": name,
            "contact_name": contact,
            "email": email,
            "phone": phone,
            "city": city,
            "country": "USA",
            "reliability_score": rel,
            "created_at": datetime.now() - timedelta(days=180)
        })
    df = pd.DataFrame(suppliers_data)
    return df

def generate_products(suppliers_df: pd.DataFrame) -> pd.DataFrame:
    """Generates 100 products across the categories linked to suppliers."""
    products_data = []
    supplier_ids = suppliers_df["supplier_id"].tolist()
    prod_counter = 1
    
    cat_items = list(CATEGORIES.items())
    
    while prod_counter <= 100:
        cat_name, item_list = cat_items[(prod_counter - 1) % len(cat_items)]
        base_name = item_list[(prod_counter - 1) // len(cat_items) % len(item_list)]
        variation = f"Series {(prod_counter % 3) + 1}" if prod_counter > len(cat_items) * len(item_list) else ""
        prod_name = f"{base_name} {variation}".strip()
        
        # Realistic cost and price
        cost = round(random.uniform(8.0, 120.0), 2)
        margin = random.uniform(1.35, 2.2)
        price = round(cost * margin, 2)
        
        reorder_point = random.choice([30, 40, 50, 60, 75, 90])
        target_stock = reorder_point * random.randint(3, 6)
        lead_time = random.choice([3, 4, 5, 7, 10, 14])
        supplier = random.choice(supplier_ids)
        
        products_data.append({
            "product_id": f"PROD-{prod_counter:03d}",
            "product_name": prod_name,
            "category": cat_name,
            "unit_price": price,
            "cost_price": cost,
            "reorder_point": reorder_point,
            "target_stock_level": target_stock,
            "lead_time_days": lead_time,
            "supplier_id": supplier,
            "created_at": datetime.now() - timedelta(days=120)
        })
        prod_counter += 1
        
    return pd.DataFrame(products_data)

def generate_inventory(products_df: pd.DataFrame) -> pd.DataFrame:
    """Generates inventory for each product, setting a realistic stockout/low stock distribution."""
    inventory_data = []
    
    for idx, row in products_df.iterrows():
        p_id = row["product_id"]
        reorder = row["reorder_point"]
        target = row["target_stock_level"]
        safety = int(reorder * 0.6)
        
        # 5% intentional stock-out for control tower monitoring
        if idx < 5:
            current = 0
            status = "OUT_OF_STOCK"
            reserved = 0
        # 15% low stock (action needed)
        elif idx < 20:
            current = random.randint(3, reorder)
            status = "LOW_STOCK"
            reserved = random.randint(0, max(0, current - 2))
        else:
            # Healthy stock
            current = random.randint(reorder + 10, target + 50)
            status = "IN_STOCK"
            reserved = random.randint(5, int(current * 0.25))
            
        available = max(0, current - reserved)
        
        inventory_data.append({
            "product_id": p_id,
            "current_stock": current,
            "reserved_stock": reserved,
            "available_stock": available,
            "reorder_point": reorder,
            "safety_stock": safety,
            "stock_status": status,
            "last_updated": datetime.now()
        })
        
    return pd.DataFrame(inventory_data)

def generate_sales_orders(products_df: pd.DataFrame, days: int = 90) -> pd.DataFrame:
    """Generates realistic daily sales orders for the last 90 days with day-of-week seasonality & demand spikes."""
    orders_data = []
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)
    
    price_lookup = dict(zip(products_df["product_id"], products_df["unit_price"]))
    product_ids = products_df["product_id"].tolist()
    
    order_id_counter = 10001
    
    # Pre-select 5 products to have occasional extreme demand spikes (for anomaly detection verification)
    spike_products = product_ids[10:15]
    spike_days = [start_date + timedelta(days=20), start_date + timedelta(days=45), start_date + timedelta(days=75)]
    
    current_d = start_date
    while current_d <= end_date:
        weekday = current_d.weekday() # 5=Sat, 6=Sun
        # Weekend sales boost
        daily_order_volume = random.randint(45, 65) if weekday >= 5 else random.randint(25, 45)
        
        # Sample products bought today
        selected_prods = random.sample(product_ids, k=min(daily_order_volume, len(product_ids)))
        
        for p_id in selected_prods:
            base_qty = random.randint(1, 8)
            
            # Inject demand spike anomaly on designated days/products
            if p_id in spike_products and current_d in spike_days:
                base_qty = random.randint(35, 60) # Massive Z-Score spike!
                
            unit_price = float(price_lookup[p_id])
            total_amt = round(base_qty * unit_price, 2)
            
            orders_data.append({
                "order_id": f"ORD-{order_id_counter}",
                "order_date": current_d,
                "product_id": p_id,
                "quantity_ordered": base_qty,
                "unit_price": unit_price,
                "total_amount": total_amt,
                "store_id": random.choice(["STORE-01", "STORE-02", "STORE-03", "ONLINE-ECOM"]),
                "customer_region": random.choice(["Northeast", "Midwest", "South", "West", "Pacific Northwest"]),
                "created_at": datetime.combine(current_d, datetime.min.time()) + timedelta(hours=random.randint(8, 20))
            })
            order_id_counter += 1
            
        current_d += timedelta(days=1)
        
    return pd.DataFrame(orders_data)

def generate_shipments(products_df: pd.DataFrame, days: int = 90) -> pd.DataFrame:
    """Generates shipment and delivery records over the past 90 days with on-time & delayed deliveries."""
    shipments_data = []
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)
    
    supplier_lookup = dict(zip(products_df["product_id"], products_df["supplier_id"]))
    lead_time_lookup = dict(zip(products_df["product_id"], products_df["lead_time_days"]))
    product_ids = products_df["product_id"].tolist()
    
    shipment_counter = 5001
    
    # Simulate replenishment shipments every 2-3 days
    current_d = start_date
    while current_d <= end_date:
        num_shipments = random.randint(4, 9)
        sampled_products = random.sample(product_ids, k=num_shipments)
        
        for p_id in sampled_products:
            supplier_id = supplier_lookup[p_id]
            nominal_lead = lead_time_lookup[p_id]
            expected_delivery = current_d + timedelta(days=nominal_lead)
            
            # Determine delivery outcome
            # If expected delivery is in the past: it's delivered or delayed
            if expected_delivery < end_date:
                # 85% on-time, 15% delayed
                is_delay_case = (random.random() < 0.15)
                
                # Check for extreme shipment delay anomaly
                if random.random() < 0.03: # 3% extreme delay anomaly
                    delay_days = random.randint(10, 18)
                    is_delayed = True
                elif is_delay_case:
                    delay_days = random.randint(2, 6)
                    is_delayed = True
                else:
                    delay_days = 0
                    is_delayed = False
                    
                actual_delivery = expected_delivery + timedelta(days=delay_days)
                actual_lead_time = (actual_delivery - current_d).days
                
                if actual_delivery <= end_date:
                    status = "DELIVERED"
                else:
                    status = "DELAYED"
            else:
                # Still in transit
                is_delayed = False
                delay_days = 0
                actual_delivery = None
                actual_lead_time = nominal_lead
                status = "IN_TRANSIT"
                
            qty_shipped = random.randint(50, 300)
            
            shipments_data.append({
                "shipment_id": f"SHP-{shipment_counter}",
                "supplier_id": supplier_id,
                "product_id": p_id,
                "quantity_shipped": qty_shipped,
                "order_date": current_d,
                "expected_delivery_date": expected_delivery,
                "actual_delivery_date": actual_delivery,
                "shipping_status": status,
                "lead_time_days": actual_lead_time,
                "is_delayed": is_delayed,
                "delay_days": delay_days,
                "created_at": datetime.combine(current_d, datetime.min.time()) + timedelta(hours=9)
            })
            shipment_counter += 1
            
        current_d += timedelta(days=random.randint(2, 3))
        
    return pd.DataFrame(shipments_data)

def save_and_load_data():
    """Generates all synthetic datasets, exports to CSV, and loads into PostgreSQL."""
    print("=" * 60)
    print("  RETAIL & SUPPLY CHAIN CONTROL TOWER - DATA GENERATOR")
    print("=" * 60)
    
    # 1. Generate Datasets
    print("[*] Generating 10 Suppliers...")
    df_suppliers = generate_suppliers()
    
    print("[*] Generating 100 Products across 6 retail categories...")
    df_products = generate_products(df_suppliers)
    
    print("[*] Generating Inventory records for 100 products...")
    df_inventory = generate_inventory(df_products)
    
    print("[*] Generating 90 Days of Sales Orders (with spikes & seasonality)...")
    df_sales = generate_sales_orders(df_products, days=90)
    
    print("[*] Generating Shipments and Supplier Deliveries...")
    df_shipments = generate_shipments(df_products, days=90)
    
    # 2. Save CSV Backups to data/
    print("[*] Saving CSV snapshots into data/ directory...")
    df_suppliers.to_csv(DATA_DIR / "suppliers.csv", index=False)
    df_products.to_csv(DATA_DIR / "products.csv", index=False)
    df_inventory.to_csv(DATA_DIR / "inventory.csv", index=False)
    df_sales.to_csv(DATA_DIR / "sales_orders.csv", index=False)
    df_shipments.to_csv(DATA_DIR / "shipments.csv", index=False)
    print(f"[✓] CSV files successfully saved in {DATA_DIR}")
    
    # 3. Load into PostgreSQL
    engine = get_engine()
    print("[*] Ingesting datasets into PostgreSQL...")
    with engine.begin() as conn:
        # Clear existing transactional tables in correct order
        conn.exec_driver_sql("TRUNCATE TABLE shipments, sales_orders, inventory, products, suppliers CASCADE;")
        
        df_suppliers.to_sql("suppliers", conn, if_exists="append", index=False)
        print(f"    -> Ingested {len(df_suppliers)} Suppliers")
        
        df_products.to_sql("products", conn, if_exists="append", index=False)
        print(f"    -> Ingested {len(df_products)} Products")
        
        df_inventory.to_sql("inventory", conn, if_exists="append", index=False)
        print(f"    -> Ingested {len(df_inventory)} Inventory records")
        
        df_sales.to_sql("sales_orders", conn, if_exists="append", index=False)
        print(f"    -> Ingested {len(df_sales)} Sales Orders")
        
        df_shipments.to_sql("shipments", conn, if_exists="append", index=False)
        print(f"    -> Ingested {len(df_shipments)} Shipments")
        
    print("[✓] All synthetic data loaded into PostgreSQL successfully!")
    print("=" * 60)

if __name__ == "__main__":
    save_and_load_data()

