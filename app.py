import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sales Dashboard - Zaimah Khan", layout="wide")

BLUE = "#1f77b4"
MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"]

st.sidebar.markdown("### Made by Zaimah Khan")
st.sidebar.markdown("---")
st.sidebar.header("Filters")

@st.cache_data
def load_data():
    df = pd.read_csv("sales data.csv.csv")
    # Clean Month if it's number
    if "Month" in df.columns:
        try:
            # Convert 1-12 to Jan-Dec if needed
            df["MonthNum"] = pd.to_numeric(df["Month"], errors='coerce')
            month_map = {i+1: m for i, m in enumerate(MONTHS)}
            df["MonthName"] = df["MonthNum"].map(month_map)
        except:
            pass
    return df

df = load_data()

# Filters - SAFE
def get_options(col):
    if col in df.columns:
        vals = sorted([str(x) for x in df[col].dropna().unique().tolist()])
        return ["All"] + vals
    return ["All"]

month_opts = get_options("Month")
city_opts = get_options("City")
product_opts = get_options("Product")

month_sel = st.sidebar.selectbox("Month", month_opts)
city_sel = st.sidebar.selectbox("City", city_opts)
product_sel = st.sidebar.selectbox("Product", product_opts)

filtered = df.copy()
if month_sel != "All" and "Month" in filtered.columns:
    filtered = filtered[filtered["Month"].astype(str) == str(month_sel)]
if city_sel != "All" and "City" in filtered.columns:
    filtered = filtered[filtered["City"].astype(str) == str(city_sel)]
if product_sel != "All" and "Product" in filtered.columns:
    filtered = filtered[filtered["Product"].astype(str) == str(product_sel)]

if filtered.empty:
    st.sidebar.warning("No data for this filter, showing all data")
    filtered = df.copy()

st.title("Electronics Store Sales Dashboard, 2019")
st.caption("Made by Zaimah Khan | 5 Business Questions")

# KPIs
if "Sales" in filtered.columns:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Sales", f"${filtered['Sales'].sum():,.0f}")
    c2.metric("Orders", f"{len(filtered):,}")
    if "Quantity Ordered" in filtered.columns:
        c3.metric("Items Sold", f"{filtered['Quantity Ordered'].sum():,}")
    else:
        c3.metric("Avg Sale", f"${filtered['Sales'].mean():.2f}")
    c4.metric("Cities", f"{filtered['City'].nunique() if 'City' in filtered.columns else 0}")

left, right = st.columns(2)

with left:
    st.subheader("Q1. Which month had the best sales?")
    if "Month" in filtered.columns and "Sales" in filtered.columns:
        monthly = filtered.groupby("Month", as_index=False)["Sales"].sum()
        # Sort by month number if possible
        if "MonthNum" in filtered.columns:
            monthly["MonthNum"] = pd.to_numeric(monthly["Month"], errors='coerce')
            monthly = monthly.sort_values("MonthNum")
        
        fig1 = px.bar(monthly, x="Month", y="Sales", color_discrete_sequence=[BLUE])
        st.plotly_chart(fig1, use_container_width=True)
        
        if not monthly.empty and monthly["Sales"].notna().any():
            try:
                best = monthly.loc[monthly["Sales"].idxmax()]
                st.success(f"Best month: **{best['Month']}** with ${best['Sales']:,.0f}")
            except:
                st.info("Best month shown in chart")

with right:
    st.subheader("Q2. Which city had highest sales?")
    if "City" in filtered.columns and "Sales" in filtered.columns:
        city_sales = filtered.groupby("City", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
        fig2 = px.bar(city_sales, x="City", y="Sales", color_discrete_sequence=[BLUE])
        st.plotly_chart(fig2, use_container_width=True)
        if not city_sales.empty:
            st.caption(f"Top City: **{city_sales.iloc[0]['City']}**")

left2, right2 = st.columns(2)

with left2:
    st.subheader("Q3. Which product sold the most?")
    if "Product" in filtered.columns and "Quantity Ordered" in filtered.columns:
        prod = filtered.groupby("Product", as_index=False)["Quantity Ordered"].sum().sort_values("Quantity Ordered", ascending=False).head(10)
        fig3 = px.bar(prod, x="Quantity Ordered", y="Product", orientation='h', color_discrete_sequence=[BLUE])
        st.plotly_chart(fig3, use_container_width=True)

with right2:
    st.subheader("Q4. Sales by Hour (When do people buy?)")
    if "Hour" in filtered.columns and "Sales" in filtered.columns:
        hourly = filtered.groupby("Hour", as_index=False)["Sales"].sum()
        fig4 = px.line(hourly, x="Hour", y="Sales", markers=True, color_discrete_sequence=[BLUE])
        st.plotly_chart(fig4, use_container_width=True)

st.subheader("Q5. Cleaned Data & Summary")
st.write(f"Showing {len(filtered):,} rows (filtered)")

# FIX: Use st.dataframe without hide_index
st.dataframe(filtered.head(100), use_container_width=True)

st.subheader("Sales by City - Table")
if "City" in filtered.columns and "Sales" in filtered.columns:
    summary = filtered.groupby("City", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
    st.table(summary)
