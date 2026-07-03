"""
generate_sample_data.py
------------------------
Creates a realistic sample inventory dataset at data/sample_inventory.csv
Run this once before starting the app (already run for you, but you can
re-run it anytime to get a fresh randomized dataset):

    python generate_sample_data.py
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

categories = {
    "Electronics": ["Wireless Mouse", "USB-C Cable", "Bluetooth Speaker", "Laptop Stand",
                     "Webcam HD", "Mechanical Keyboard", "Power Bank", "HDMI Adapter"],
    "Office Supplies": ["A4 Paper Ream", "Stapler", "Sticky Notes", "Ballpoint Pens (Box)",
                         "Whiteboard Markers", "Binder Clips", "File Folders", "Desk Organizer"],
    "Furniture": ["Office Chair", "Standing Desk", "Bookshelf", "Filing Cabinet",
                  "Monitor Arm", "Cable Tray"],
    "Kitchen & Pantry": ["Coffee Pods (Box)", "Bottled Water Case", "Paper Cups",
                         "Instant Noodles", "Tea Bags Box", "Sugar Sachets"],
    "Cleaning Supplies": ["Hand Sanitizer", "Disinfectant Spray", "Paper Towels",
                          "Trash Bags Roll", "Glass Cleaner"],
    "Packaging": ["Cardboard Boxes (M)", "Bubble Wrap Roll", "Packing Tape",
                  "Shipping Labels", "Poly Mailers (Pack)"],
}

suppliers = ["Acme Distributors", "NorthStar Supply Co.", "Global Parts Ltd.",
             "BrightWay Wholesale", "Metro Logistics", "Prime Vendor Group"]

locations = ["Warehouse A", "Warehouse B", "Store Room 1", "Store Room 2", "Main DC"]

rows = []
item_id = 1000

for category, items in categories.items():
    for item in items:
        supplier = random.choice(suppliers)
        location = random.choice(locations)
        unit_cost = round(np.random.uniform(1.5, 250), 2)
        markup = np.random.uniform(1.2, 1.8)
        unit_price = round(unit_cost * markup, 2)
        reorder_level = random.randint(10, 50)

        # Bias some items to be low stock / out of stock for a realistic alert view
        stock_roll = random.random()
        if stock_roll < 0.12:
            quantity = random.randint(0, reorder_level - 1)          # low / critical stock
        elif stock_roll < 0.20:
            quantity = 0                                              # out of stock
        else:
            quantity = random.randint(reorder_level, reorder_level * 6)  # healthy stock

        last_restocked = datetime.now() - timedelta(days=random.randint(1, 180))

        rows.append({
            "Item_ID": f"SKU-{item_id}",
            "Item_Name": item,
            "Category": category,
            "Supplier": supplier,
            "Location": location,
            "Quantity": quantity,
            "Reorder_Level": reorder_level,
            "Unit_Cost": unit_cost,
            "Unit_Price": unit_price,
            "Last_Restocked": last_restocked.strftime("%Y-%m-%d"),
        })
        item_id += 1

df = pd.DataFrame(rows)
df.to_csv("data/sample_inventory.csv", index=False)
print(f"Sample inventory data generated: {len(df)} items -> data/sample_inventory.csv")
