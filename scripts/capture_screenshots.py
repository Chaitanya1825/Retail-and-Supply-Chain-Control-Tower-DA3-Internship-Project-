"""
Script to capture high-resolution screenshots of the SUPPLYCORE Control Tower dashboard.
Uses Playwright to navigate through all tabs and save 1920x1080 screenshots in docs/screenshots/.
"""
import os
import time
from playwright.sync_api import sync_playwright

OUTPUT_DIR = os.path.abspath("docs/screenshots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

TABS = [
    ("Overview", "01_overview_dashboard.png"),
    ("Inventory", "02_inventory_monitor.png"),
    ("Shipments", "03_shipment_logistics.png"),
    ("Demand Forecast", "04_demand_forecasting.png"),
    ("Anomalies", "05_anomaly_detection.png"),
    ("What-if Analysis", "06_what_if_simulation.png"),
]

def capture_dashboard_screenshots():
    print(f"[*] Starting screenshot capture at 1920x1080 -> {OUTPUT_DIR}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Create context with dark color scheme and 1920x1080 viewport
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            color_scheme="dark",
            device_scale_factor=1.25  # Crisp retina-like scaling
        )
        page = context.new_page()
        
        print("[*] Loading http://localhost:8501...")
        page.goto("http://localhost:8501", timeout=30000, wait_until="networkidle")
        time.sleep(3)  # Wait for initial render and animations
        
        for tab_name, filename in TABS:
            print(f"[*] Navigating to tab: '{tab_name}'...")
            try:
                # Find and click the radio option with text matching tab_name
                # Streamlit radio labels can be selected by text or role
                locator = page.locator(f"text='{tab_name}'").first
                locator.click(timeout=5000)
                time.sleep(3)  # Allow Plotly charts and tables to render fully
            except Exception as e:
                print(f"[!] Warning while clicking tab '{tab_name}': {e}")
                
            filepath = os.path.join(OUTPUT_DIR, filename)
            # Take full viewport screenshot
            page.screenshot(path=filepath, full_page=False)
            print(f"[✓] Saved screenshot: {filename} ({os.path.getsize(filepath) / 1024:.1f} KB)")
            
        browser.close()
    print("[✓] All screenshots captured successfully!")

if __name__ == "__main__":
    capture_dashboard_screenshots()

