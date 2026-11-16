-- Retail and Supply Chain Control Tower Schema
-- PostgreSQL DDL

DROP VIEW IF EXISTS v_what_if_delay_impact CASCADE;
DROP VIEW IF EXISTS v_anomaly_feed CASCADE;
DROP VIEW IF EXISTS v_demand_forecast_summary CASCADE;
DROP VIEW IF EXISTS v_shipment_performance CASCADE;
DROP VIEW IF EXISTS v_inventory_status CASCADE;
DROP VIEW IF EXISTS v_kpi_summary CASCADE;

-- 1. Suppliers Table
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id VARCHAR(20) PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL,
    contact_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(50),
    city VARCHAR(50),
    country VARCHAR(50) DEFAULT 'USA',
    reliability_score NUMERIC(5, 2) DEFAULT 95.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Products Table
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    cost_price NUMERIC(10, 2) NOT NULL,
    reorder_point INT NOT NULL DEFAULT 50,
    target_stock_level INT NOT NULL DEFAULT 250,
    lead_time_days INT NOT NULL DEFAULT 7,
    supplier_id VARCHAR(20) REFERENCES suppliers(supplier_id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Inventory Table
CREATE TABLE IF NOT EXISTS inventory (
    inventory_id SERIAL PRIMARY KEY,
    product_id VARCHAR(20) UNIQUE NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    current_stock INT NOT NULL DEFAULT 0,
    reserved_stock INT NOT NULL DEFAULT 0,
    available_stock INT NOT NULL DEFAULT 0,
    reorder_point INT NOT NULL DEFAULT 50,
    safety_stock INT NOT NULL DEFAULT 30,
    stock_status VARCHAR(20) NOT NULL DEFAULT 'IN_STOCK', -- 'IN_STOCK', 'LOW_STOCK', 'OUT_OF_STOCK'
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Sales Orders Table (Last 90 days history)
CREATE TABLE IF NOT EXISTS sales_orders (
    order_id VARCHAR(30) PRIMARY KEY,
    order_date DATE NOT NULL,
    product_id VARCHAR(20) NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    quantity_ordered INT NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    total_amount NUMERIC(12, 2) NOT NULL,
    store_id VARCHAR(20) DEFAULT 'STORE-01',
    customer_region VARCHAR(50) DEFAULT 'North America',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Shipments Table
CREATE TABLE IF NOT EXISTS shipments (
    shipment_id VARCHAR(30) PRIMARY KEY,
    supplier_id VARCHAR(20) NOT NULL REFERENCES suppliers(supplier_id) ON DELETE CASCADE,
    product_id VARCHAR(20) NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    quantity_shipped INT NOT NULL,
    order_date DATE NOT NULL,
    expected_delivery_date DATE NOT NULL,
    actual_delivery_date DATE,
    shipping_status VARCHAR(20) NOT NULL DEFAULT 'IN_TRANSIT', -- 'DELIVERED', 'IN_TRANSIT', 'DELAYED'
    lead_time_days INT,
    is_delayed BOOLEAN DEFAULT FALSE,
    delay_days INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Overall Control Tower KPI Metrics
CREATE TABLE IF NOT EXISTS kpi_metrics (
    metric_id SERIAL PRIMARY KEY,
    calculation_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    stock_out_rate NUMERIC(6, 2) NOT NULL,        -- Percentage e.g. 5.00%
    on_time_delivery_pct NUMERIC(6, 2) NOT NULL,  -- Percentage e.g. 92.50%
    avg_supplier_lead_time NUMERIC(6, 2) NOT NULL,-- In days e.g. 6.4 days
    avg_days_of_inventory NUMERIC(6, 2) NOT NULL, -- Days of Inventory Remaining e.g. 24.3 days
    total_products_monitored INT NOT NULL,
    out_of_stock_products INT NOT NULL,
    delayed_shipments_count INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Product Level KPIs & Days of Inventory
CREATE TABLE IF NOT EXISTS product_kpis (
    product_id VARCHAR(20) PRIMARY KEY REFERENCES products(product_id) ON DELETE CASCADE,
    product_name VARCHAR(150),
    category VARCHAR(50),
    current_stock INT NOT NULL,
    avg_daily_demand_30d NUMERIC(10, 2) NOT NULL DEFAULT 1.0,
    days_of_inventory_remaining NUMERIC(10, 2) NOT NULL DEFAULT 0.0,
    is_stock_out BOOLEAN DEFAULT FALSE,
    reorder_recommended BOOLEAN DEFAULT FALSE,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Anomaly Detection Table (Z-Score outliers)
CREATE TABLE IF NOT EXISTS anomalies (
    anomaly_id SERIAL PRIMARY KEY,
    anomaly_type VARCHAR(30) NOT NULL, -- 'DEMAND_SPIKE', 'SHIPMENT_DELAY'
    reference_id VARCHAR(50) NOT NULL,  -- order_id, shipment_id, or product_id
    entity_name VARCHAR(150) NOT NULL,
    metric_value NUMERIC(10, 2) NOT NULL,
    baseline_mean NUMERIC(10, 2) NOT NULL,
    baseline_std NUMERIC(10, 2) NOT NULL,
    z_score NUMERIC(6, 2) NOT NULL,
    severity VARCHAR(20) NOT NULL,      -- 'HIGH', 'CRITICAL'
    details TEXT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'OPEN'
);

-- 9. Demand Forecasts Table (Prophet 7-day forecasts)
CREATE TABLE IF NOT EXISTS demand_forecasts (
    forecast_id SERIAL PRIMARY KEY,
    product_id VARCHAR(20) NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    forecast_date DATE NOT NULL,
    predicted_demand NUMERIC(10, 2) NOT NULL,
    confidence_lower NUMERIC(10, 2) NOT NULL,
    confidence_upper NUMERIC(10, 2) NOT NULL,
    current_stock INT NOT NULL,
    projected_stock_remaining NUMERIC(10, 2) NOT NULL,
    stockout_risk BOOLEAN DEFAULT FALSE,
    model_name VARCHAR(50) DEFAULT 'Prophet-v1.5',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_product_forecast_date UNIQUE (product_id, forecast_date)
);

-- 10. What-If Scenario Analysis Table (7-Day Delay Simulation)
CREATE TABLE IF NOT EXISTS what_if_scenarios (
    scenario_id SERIAL PRIMARY KEY,
    scenario_name VARCHAR(50) NOT NULL, -- '7_DAY_SUPPLIER_DELAY'
    product_id VARCHAR(20) NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    supplier_id VARCHAR(20) REFERENCES suppliers(supplier_id) ON DELETE CASCADE,
    product_name VARCHAR(150),
    category VARCHAR(50),
    original_lead_time_days INT NOT NULL,
    simulated_lead_time_days INT NOT NULL,
    current_inventory INT NOT NULL,
    expected_demand_during_delay NUMERIC(10, 2) NOT NULL,
    projected_stockout_risk BOOLEAN DEFAULT FALSE,
    estimated_units_shortage INT DEFAULT 0,
    impact_severity VARCHAR(20) NOT NULL, -- 'NONE', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. Alerts Log Table
CREATE TABLE IF NOT EXISTS alert_logs (
    alert_id SERIAL PRIMARY KEY,
    alert_type VARCHAR(30) NOT NULL, -- 'CRITICAL_STOCK', 'SHIPMENT_DELAY'
    severity VARCHAR(20) NOT NULL,   -- 'WARNING', 'CRITICAL'
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    recipient VARCHAR(100),
    delivery_status VARCHAR(20) DEFAULT 'LOGGED_ONLY', -- 'SENT', 'LOGGED_ONLY', 'FAILED'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance indices
CREATE INDEX IF NOT EXISTS idx_sales_orders_date_prod ON sales_orders(order_date, product_id);
CREATE INDEX IF NOT EXISTS idx_shipments_supplier_prod ON shipments(supplier_id, product_id);
CREATE INDEX IF NOT EXISTS idx_demand_forecasts_date ON demand_forecasts(forecast_date);
CREATE INDEX IF NOT EXISTS idx_anomalies_type ON anomalies(anomaly_type, detected_at);

