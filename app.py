import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sales Dashboard - Zaimah Khan", layout="wide")

st.sidebar.markdown("### Made by Zaimah Khan")
st.sidebar.markdown("---")

@st.cache_data
def load_data():
    try:
        return pd.read_csv("sales data.csv.csv")
    except:
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.error("Sales Data.csv nahi mila! Please upload in GitHub.")
    st.stop()

uploaded = st.sidebar.file_uploader("Upload Sales Data.csv (optional)", type=["csv"])
if uploaded is not None:
    df = pd.read_csv(uploaded)

st.sidebar.header("Filters")

def get_options(col):
    if col in df.columns:
        vals = sorted(df[col].dropna().unique().tolist())
        return ["All"] + vals
    return ["All"]

month_options = get_options("Month")
city_options = get_options("City")
product_options = get_options("Product")

month_sel = st.sidebar.selectbox("Month", month_options)
city_sel = st.sidebar.selectbox("City", city_options)
product_sel = st.sidebar.selectbox("Product", product_options)

filtered = df.copy()
if month_sel != "All" and "Month" in filtered.columns:
    filtered = filtered[filtered["Month"] == month_sel]
if city_sel != "All" and "City" in filtered.columns:
    filtered = filtered[filtered["City"] == city_sel]
if product_sel != "All" and "Product" in filtered.columns:
    filtered = filtered[filtered["Product"] == product_sel]

if filtered.empty:
    st.sidebar.warning("No data for this filter, showing all data")
    filtered = df.copy()

st.title("Electronics Store Sales Dashboard, 2019")
st.caption("Made by Zaimah Khan | Student Project")

if "Sales" in filtered.columns:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total sales", f"${filtered['Sales'].sum():,.0f}")
    c2.metric("Orders", f"{len(filtered):,}")
    if "Quantity" in filtered.columns:
        c3.metric("Items sold", f"{filtered['Quantity'].sum():,}")
    c4.metric("Average order", f"${filtered['Sales'].mean():.2f}")

st.subheader("Q1. Which month had the best sales?")
if "Month" in filtered.columns and "Sales" in filtered.columns:
    monthly = filtered.groupby("Month", as_index=False)["Sales"].sum()
    if not monthly.empty:
        fig = px.bar(monthly, x="Month", y="Sales")
        st.plotly_chart(fig, use_container_width=True)
        if monthly["Sales"].notna().any():
            best = monthly.loc[monthly["Sales"].idxmax()]
            st.success(f"Best month: {best['Month']} with ${best['Sales']:,.0f}")

st.subheader("Cleaned data (first 100 rows)")
st.table(filtered.head(100))

if "City" in filtered.columns and "Sales" in filtered.columns:
    st.subheader("Sales by City")
    city_sales = filtered.groupby("City", as_index=False)["Sales"].sum()
    st.table(city_sales)
