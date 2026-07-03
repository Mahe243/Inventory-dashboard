"""
Inventory Management Dashboard
--------------------------------
Streamlit + Plotly dashboard covering:
  1. Stock Levels
  2. Low Stock Alerts
  3. Category Analysis
  4. Supplier Analysis
  5. Inventory Valuation

Run:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

# --------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Inventory Management Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).parent / "data" / "sample_inventory.csv"

REQUIRED_COLUMNS = [
    "Item_ID", "Item_Name", "Category", "Supplier", "Location",
    "Quantity", "Reorder_Level", "Unit_Cost", "Unit_Price", "Last_Restocked",
]

# --------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------
@st.cache_data
def load_data(path_or_buffer) -> pd.DataFrame:
    df = pd.read_csv(path_or_buffer)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Uploaded file is missing required columns: {missing}")

    df["Last_Restocked"] = pd.to_datetime(df["Last_Restocked"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(0)
    df["Reorder_Level"] = pd.to_numeric(df["Reorder_Level"], errors="coerce").fillna(0)
    df["Unit_Cost"] = pd.to_numeric(df["Unit_Cost"], errors="coerce").fillna(0)
    df["Unit_Price"] = pd.to_numeric(df["Unit_Price"], errors="coerce").fillna(0)

    df["Stock_Value"] = df["Quantity"] * df["Unit_Cost"]
    df["Retail_Value"] = df["Quantity"] * df["Unit_Price"]
    df["Potential_Margin"] = df["Retail_Value"] - df["Stock_Value"]

    def status(row):
        if row["Quantity"] <= 0:
            return "Out of Stock"
        elif row["Quantity"] <= row["Reorder_Level"]:
            return "Low Stock"
        elif row["Quantity"] <= row["Reorder_Level"] * 2:
            return "Adequate"
        return "Overstocked"

    df["Stock_Status"] = df.apply(status, axis=1)
    return df


# --------------------------------------------------------------------------
# Sidebar: data source + filters
# --------------------------------------------------------------------------
st.sidebar.title("📦 Inventory Dashboard")
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader("Upload your own inventory CSV", type=["csv"])
st.sidebar.caption(
    "Expected columns: " + ", ".join(REQUIRED_COLUMNS)
)

try:
    if uploaded_file is not None:
        data = load_data(uploaded_file)
        st.sidebar.success(f"Loaded {len(data)} items from uploaded file.")
    else:
        data = load_data(DATA_PATH)
        st.sidebar.info(f"Using sample data ({len(data)} items). Upload a CSV to use your own.")
except Exception as e:
    st.sidebar.error(f"Could not load file: {e}")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.subheader("Filters")

categories_sel = st.sidebar.multiselect(
    "Category", options=sorted(data["Category"].unique()), default=None
)
suppliers_sel = st.sidebar.multiselect(
    "Supplier", options=sorted(data["Supplier"].unique()), default=None
)
status_sel = st.sidebar.multiselect(
    "Stock Status",
    options=["Out of Stock", "Low Stock", "Adequate", "Overstocked"],
    default=None,
)

filtered = data.copy()
if categories_sel:
    filtered = filtered[filtered["Category"].isin(categories_sel)]
if suppliers_sel:
    filtered = filtered[filtered["Supplier"].isin(suppliers_sel)]
if status_sel:
    filtered = filtered[filtered["Stock_Status"].isin(status_sel)]

if filtered.empty:
    st.warning("No items match the selected filters. Adjust filters in the sidebar.")
    st.stop()

# --------------------------------------------------------------------------
# Header + KPI row
# --------------------------------------------------------------------------
st.title("📦 Inventory Management Dashboard")
st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total SKUs", f"{filtered['Item_ID'].nunique():,}")
k2.metric("Total Units in Stock", f"{int(filtered['Quantity'].sum()):,}")
k3.metric("Inventory Value (Cost)", f"${filtered['Stock_Value'].sum():,.2f}")
k4.metric("Inventory Value (Retail)", f"${filtered['Retail_Value'].sum():,.2f}")
low_count = filtered[filtered["Stock_Status"].isin(["Low Stock", "Out of Stock"])].shape[0]
k5.metric("Low / Out of Stock Items", f"{low_count}", delta=None,
          delta_color="inverse")

st.markdown("---")

# --------------------------------------------------------------------------
# Tabs
# --------------------------------------------------------------------------
tab_stock, tab_alerts, tab_category, tab_supplier, tab_valuation = st.tabs(
    ["📊 Stock Levels", "🚨 Low Stock Alerts", "🗂️ Category Analysis",
     "🏭 Supplier Analysis", "💰 Inventory Valuation"]
)

# ---------------------------- TAB 1: STOCK LEVELS -------------------------
with tab_stock:
    st.subheader("Stock Levels by Item")

    col1, col2 = st.columns([2, 1])

    with col1:
        sorted_df = filtered.sort_values("Quantity", ascending=True)
        fig = px.bar(
            sorted_df,
            x="Quantity",
            y="Item_Name",
            color="Stock_Status",
            orientation="h",
            color_discrete_map={
                "Out of Stock": "#d62728",
                "Low Stock": "#ff7f0e",
                "Adequate": "#2ca02c",
                "Overstocked": "#1f77b4",
            },
            height=max(400, len(sorted_df) * 22),
            title="Current Quantity on Hand by Item",
        )
        fig.add_vline(x=0, line_width=1, line_color="gray")
        fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        status_counts = filtered["Stock_Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig_donut = px.pie(
            status_counts, names="Status", values="Count", hole=0.55,
            color="Status",
            color_discrete_map={
                "Out of Stock": "#d62728",
                "Low Stock": "#ff7f0e",
                "Adequate": "#2ca02c",
                "Overstocked": "#1f77b4",
            },
            title="Stock Status Breakdown",
        )
        fig_donut.update_layout(margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig_donut, use_container_width=True)

        fig_days = px.histogram(
            filtered,
            x=(pd.Timestamp.now() - filtered["Last_Restocked"]).dt.days,
            nbins=15,
            title="Days Since Last Restock",
            labels={"x": "Days"},
        )
        fig_days.update_layout(margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig_days, use_container_width=True)

    st.subheader("Full Stock Table")
    st.dataframe(
        filtered[["Item_ID", "Item_Name", "Category", "Supplier", "Location",
                  "Quantity", "Reorder_Level", "Stock_Status", "Last_Restocked"]]
        .sort_values("Quantity"),
        use_container_width=True,
        hide_index=True,
    )

# --------------------------- TAB 2: LOW STOCK ALERTS -----------------------
with tab_alerts:
    st.subheader("🚨 Low Stock & Out-of-Stock Alerts")

    alerts_df = filtered[filtered["Stock_Status"].isin(["Low Stock", "Out of Stock"])].copy()
    alerts_df["Units_Below_Reorder"] = alerts_df["Reorder_Level"] - alerts_df["Quantity"]
    alerts_df = alerts_df.sort_values("Units_Below_Reorder", ascending=False)

    if alerts_df.empty:
        st.success("✅ No items are currently low or out of stock. Great job!")
    else:
        a1, a2 = st.columns(2)
        a1.metric("Items Needing Reorder", f"{len(alerts_df)}")
        est_cost = (alerts_df["Reorder_Level"] * 2 - alerts_df["Quantity"]).clip(lower=0) * alerts_df["Unit_Cost"]
        a2.metric("Est. Cost to Restock to 2x Reorder Level", f"${est_cost.sum():,.2f}")

        fig_alert = px.bar(
            alerts_df,
            x="Units_Below_Reorder",
            y="Item_Name",
            color="Stock_Status",
            orientation="h",
            color_discrete_map={"Out of Stock": "#d62728", "Low Stock": "#ff7f0e"},
            title="Units Below Reorder Level (higher = more urgent)",
            height=max(350, len(alerts_df) * 28),
        )
        fig_alert.update_layout(margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig_alert, use_container_width=True)

        st.markdown("#### Reorder List")

        def highlight_status(row):
            color = "#ffcccc" if row["Stock_Status"] == "Out of Stock" else "#ffe5cc"
            return [f"background-color: {color}"] * len(row)

        display_cols = ["Item_ID", "Item_Name", "Category", "Supplier", "Quantity",
                         "Reorder_Level", "Units_Below_Reorder", "Stock_Status"]
        st.dataframe(
            alerts_df[display_cols].style.apply(highlight_status, axis=1),
            use_container_width=True,
            hide_index=True,
        )

        csv = alerts_df[display_cols].to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Reorder List (CSV)", csv,
                            "reorder_list.csv", "text/csv")

# --------------------------- TAB 3: CATEGORY ANALYSIS -----------------------
with tab_category:
    st.subheader("Category Analysis")

    cat_summary = filtered.groupby("Category").agg(
        SKUs=("Item_ID", "nunique"),
        Total_Units=("Quantity", "sum"),
        Stock_Value=("Stock_Value", "sum"),
        Retail_Value=("Retail_Value", "sum"),
        Avg_Unit_Cost=("Unit_Cost", "mean"),
    ).reset_index().sort_values("Stock_Value", ascending=False)

    c1, c2 = st.columns(2)
    with c1:
        fig_cat_val = px.bar(
            cat_summary, x="Category", y="Stock_Value",
            color="Category", title="Inventory Value (Cost) by Category",
            text_auto=".2s",
        )
        fig_cat_val.update_layout(showlegend=False, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig_cat_val, use_container_width=True)

    with c2:
        fig_cat_units = px.pie(
            cat_summary, names="Category", values="Total_Units",
            title="Unit Distribution by Category", hole=0.4,
        )
        fig_cat_units.update_layout(margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig_cat_units, use_container_width=True)

    st.markdown("#### Stock Status Composition by Category")
    status_by_cat = filtered.groupby(["Category", "Stock_Status"]).size().reset_index(name="Count")
    fig_stack = px.bar(
        status_by_cat, x="Category", y="Count", color="Stock_Status",
        barmode="stack",
        color_discrete_map={
            "Out of Stock": "#d62728", "Low Stock": "#ff7f0e",
            "Adequate": "#2ca02c", "Overstocked": "#1f77b4",
        },
        title="Item Count by Stock Status, per Category",
    )
    fig_stack.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig_stack, use_container_width=True)

    st.markdown("#### Category Summary Table")
    st.dataframe(
        cat_summary.style.format({
            "Stock_Value": "${:,.2f}", "Retail_Value": "${:,.2f}", "Avg_Unit_Cost": "${:,.2f}"
        }),
        use_container_width=True, hide_index=True,
    )

# --------------------------- TAB 4: SUPPLIER ANALYSIS -----------------------
with tab_supplier:
    st.subheader("Supplier Analysis")

    sup_summary = filtered.groupby("Supplier").agg(
        SKUs=("Item_ID", "nunique"),
        Total_Units=("Quantity", "sum"),
        Stock_Value=("Stock_Value", "sum"),
        Avg_Unit_Cost=("Unit_Cost", "mean"),
        Low_Stock_Items=("Stock_Status", lambda s: (s.isin(["Low Stock", "Out of Stock"])).sum()),
    ).reset_index().sort_values("Stock_Value", ascending=False)

    s1, s2 = st.columns(2)
    with s1:
        fig_sup_val = px.bar(
            sup_summary, x="Stock_Value", y="Supplier", orientation="h",
            color="Stock_Value", color_continuous_scale="Blues",
            title="Inventory Value (Cost) by Supplier",
        )
        fig_sup_val.update_layout(margin=dict(l=10, r=10, t=50, b=10), coloraxis_showscale=False)
        st.plotly_chart(fig_sup_val, use_container_width=True)

    with s2:
        fig_sup_risk = px.bar(
            sup_summary, x="Supplier", y="Low_Stock_Items",
            color="Low_Stock_Items", color_continuous_scale="Reds",
            title="Low / Out-of-Stock Items per Supplier (Risk)",
        )
        fig_sup_risk.update_layout(margin=dict(l=10, r=10, t=50, b=10), coloraxis_showscale=False)
        st.plotly_chart(fig_sup_risk, use_container_width=True)

    fig_scatter = px.scatter(
        sup_summary, x="SKUs", y="Stock_Value", size="Total_Units",
        color="Supplier", hover_name="Supplier",
        title="Supplier Footprint: SKUs vs Inventory Value (bubble = total units)",
    )
    fig_scatter.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("#### Supplier Summary Table")
    st.dataframe(
        sup_summary.style.format({"Stock_Value": "${:,.2f}", "Avg_Unit_Cost": "${:,.2f}"}),
        use_container_width=True, hide_index=True,
    )

# --------------------------- TAB 5: INVENTORY VALUATION ---------------------
with tab_valuation:
    st.subheader("Inventory Valuation")

    v1, v2, v3 = st.columns(3)
    v1.metric("Total Cost Value", f"${filtered['Stock_Value'].sum():,.2f}")
    v2.metric("Total Retail Value", f"${filtered['Retail_Value'].sum():,.2f}")
    v3.metric("Potential Margin", f"${filtered['Potential_Margin'].sum():,.2f}")

    fig_treemap = px.treemap(
        filtered,
        path=["Category", "Item_Name"],
        values="Stock_Value",
        color="Stock_Value",
        color_continuous_scale="Viridis",
        title="Inventory Value Breakdown (Category → Item)",
    )
    fig_treemap.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig_treemap, use_container_width=True)

    top_n = st.slider("Show Top N Items by Value", min_value=5,
                       max_value=min(30, len(filtered)), value=min(10, len(filtered)))
    top_items = filtered.sort_values("Stock_Value", ascending=False).head(top_n)

    fig_top = px.bar(
        top_items.sort_values("Stock_Value"),
        x="Stock_Value", y="Item_Name", orientation="h",
        color="Category",
        title=f"Top {top_n} Items by Inventory Value (Cost)",
        text_auto=".2s",
    )
    fig_top.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig_top, use_container_width=True)

    st.markdown("#### Cost vs Retail Value Comparison")
    fig_cost_retail = go.Figure()
    fig_cost_retail.add_trace(go.Bar(
        x=cat_summary["Category"] if 'cat_summary' in dir() else filtered["Category"].unique(),
        y=filtered.groupby("Category")["Stock_Value"].sum(),
        name="Cost Value", marker_color="#636EFA",
    ))
    fig_cost_retail.add_trace(go.Bar(
        x=filtered.groupby("Category")["Retail_Value"].sum().index,
        y=filtered.groupby("Category")["Retail_Value"].sum(),
        name="Retail Value", marker_color="#EF553B",
    ))
    fig_cost_retail.update_layout(
        barmode="group", title="Cost vs Retail Value by Category",
        margin=dict(l=10, r=10, t=50, b=10),
    )
    st.plotly_chart(fig_cost_retail, use_container_width=True)

    st.markdown("#### Full Valuation Table")
    st.dataframe(
        filtered[["Item_ID", "Item_Name", "Category", "Supplier", "Quantity",
                  "Unit_Cost", "Unit_Price", "Stock_Value", "Retail_Value", "Potential_Margin"]]
        .sort_values("Stock_Value", ascending=False)
        .style.format({
            "Unit_Cost": "${:,.2f}", "Unit_Price": "${:,.2f}",
            "Stock_Value": "${:,.2f}", "Retail_Value": "${:,.2f}", "Potential_Margin": "${:,.2f}",
        }),
        use_container_width=True, hide_index=True,
    )

    csv_val = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Full Inventory Data (CSV)", csv_val,
                        "inventory_valuation.csv", "text/csv")

st.markdown("---")
st.caption("Inventory Management Dashboard · Built with Streamlit + Plotly")
