# 📦 Inventory Management Dashboard

A Streamlit + Plotly dashboard for tracking stock levels, low-stock alerts,
category analysis, supplier analysis, and inventory valuation.

## 🌐 Live Demo

**Try the live application here:**  
https://inventory-dashboard-njebgc9mvmjcvcbnr97pkx.streamlit.app/

## Folder Structure

```
inventory_dashboard/
├── app.py                     # Main Streamlit application
├── generate_sample_data.py    # Generates data/sample_inventory.csv
├── requirements.txt           # Python dependencies
├── README.md
└── data/
    └── sample_inventory.csv   # Sample dataset (auto-generated, already included)
```

## Setup (VS Code / local machine)

1. Open the `inventory_dashboard` folder in VS Code.
2. Create and activate a virtual environment (recommended):

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Regenerate the sample dataset:

   ```bash
   python generate_sample_data.py
   ```

5. Run the app:

   ```bash
   streamlit run app.py
   ```

6. Streamlit will open automatically at **http://localhost:8501**. If it doesn't,
   open that URL in your browser manually.

## Using Your Own Data

Use the **"Upload your own inventory CSV"** control in the sidebar. Your file
must include these columns:

| Column          | Description                          |
|-----------------|---------------------------------------|
| Item_ID         | Unique SKU / identifier               |
| Item_Name       | Product name                          |
| Category        | Product category                      |
| Supplier        | Supplier / vendor name                |
| Location        | Storage location / warehouse          |
| Quantity        | Units currently in stock              |
| Reorder_Level   | Threshold that triggers a reorder     |
| Unit_Cost       | Cost per unit                         |
| Unit_Price      | Selling price per unit                |
| Last_Restocked  | Date last restocked (YYYY-MM-DD)      |

## Dashboard Sections

- **📊 Stock Levels** — quantity on hand per item, status breakdown, restock recency.
- **🚨 Low Stock Alerts** — items at/under reorder level, urgency ranking, downloadable reorder list.

## Proof of Execution
<img width="1914" height="937" alt="Screenshot 2026-07-03 165241" src="https://github.com/user-attachments/assets/a075af51-0efd-4bf6-8f4b-da768c772b3c" />
<img width="1902" height="951" alt="Screenshot 2026-07-03 165319" src="https://github.com/user-attachments/assets/b322ac7b-0098-46f3-bf87-b97394d4d614" />
<img width="1916" height="944" alt="Screenshot 2026-07-03 165257" src="https://github.com/user-attachments/assets/24519460-ab48-4a72-8f27-10dff9023f68" />

- **🗂️ Category Analysis** — value and unit distribution across categories, stock-status composition.
- **🏭 Supplier Analysis** — value and risk exposure per supplier, SKU footprint.
- **💰 Inventory Valuation** — total cost/retail value, treemap breakdown, top items by value, cost vs. retail comparison.

All sections respect the **Category / Supplier / Stock Status** filters in the sidebar.
