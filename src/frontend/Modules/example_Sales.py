import streamlit as st

from backend.example_sales import (
    calculate_sales_metrics,
    get_monthly_sales,
    get_sales_by_category,
    get_sales_data,
)

# ---------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------
title = "example Sales"
icon = ":material/euro:"

# ---------------------------------------
# PAGE ELEMENTS
# ---------------------------------------
st.title("📈 Sales Dashboard")

# Get data
sales_data = get_sales_data()
metrics = calculate_sales_metrics(sales_data)

# Display key metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Sales", f"${metrics['total']:,.0f}")
with col2:
    st.metric("Average Sale", f"${metrics['average']:.2f}")
with col3:
    st.metric("Best Month", metrics["best_month"])
with col4:
    st.metric("Growth", f"{metrics['growth']:.1f}%")

# Monthly sales chart
st.subheader("Monthly Sales Trend")
st.line_chart(get_monthly_sales(sales_data))

# Sales by category
st.subheader("Sales by Category")
st.bar_chart(get_sales_by_category(sales_data))

# Raw data table
if st.checkbox("Show detailed sales data"):
    st.dataframe(sales_data)
