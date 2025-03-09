import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Path relatif untuk file CSV
file_path = os.path.join(os.path.dirname(__file__), "all_data.csv")

# Load Data
@st.cache_data
def load_data(file_path):
    if os.path.exists(file_path):
        data = pd.read_csv(file_path)
        data['order_date'] = pd.to_datetime(data['order_purchase_timestamp'])
        data['order_date_month'] = data['order_date'].dt.to_period('M')
        return data
    else:
        st.error(f"File not found at {file_path}")
        return pd.DataFrame()  # Mengembalikan DataFrame kosong

data = load_data(file_path)

# Sidebar
st.sidebar.title("Dashboard")
st.sidebar.image("https://cubic.id/public/front/images/jurnals/eZqeYWHjdJBp7DfAnCneMAh5h5B6F75s4dRS0iUL.jpeg")

# Date input dengan pengecekan data
if not data.empty:
    min_date = data['order_date'].min().date()
    max_date = data['order_date'].max().date()
    start_date, end_date = st.sidebar.date_input(
        "Select Date Range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)

    data_filtered = data[(data['order_date'] >= start_date) & (data['order_date'] <= end_date)]

    if data_filtered.empty:
        st.warning("No data available for the selected date range.")
else:
    st.stop()

# Helper Functions
def create_daily_orders_df(df):
    daily_orders_df = df.resample('D', on='order_date').agg({
        "order_id": "nunique",
        "price": "sum"
    }).reset_index()
    daily_orders_df.rename(columns={"order_id": "order_count", "price": "revenue"}, inplace=True)
    return daily_orders_df

def create_sum_order_items_df(df):
    return df.groupby("product_category_name_english").size().reset_index(name='quantity').sort_values(by='quantity', ascending=False)

# Tabs
st.title("E-commerce Public Brazil Dashboard :sparkles:")

tab1, tab2, tab3 = st.tabs(["Sales Performance", "Top Products", "Customer Insights"])

# Sales Performance Tab
with tab1:
    st.header("Sales Performance")
    daily_orders = create_daily_orders_df(data_filtered)

    col1, col2 = st.columns(2)
    with col1:
        total_orders = daily_orders['order_count'].sum()
        st.metric("Total Orders", value=total_orders)

    with col2:
        total_sales = daily_orders['revenue'].sum()
        st.metric("Total Sales", value=f"${total_sales:,.2f}")

    # Monthly Sales
    monthly_sales = data_filtered.groupby(data_filtered['order_date'].dt.to_period('M'))['order_id'].count()
    fig, ax = plt.subplots()
    monthly_sales.plot(kind='line', marker='o', ax=ax)
    ax.set_title("Monthly Sales Performance")
    st.pyplot(fig)

    # Top Cities
    st.subheader("Top 10 Cities with Highest Number of Orders")
    city_orders = data_filtered.groupby('customer_city')['order_id'].count().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=city_orders.values, y=city_orders.index, palette='Blues_r', ax=ax)
    ax.set_title("Top 10 Cities with Highest Number of Orders")
    st.pyplot(fig)

# Top Products Tab
with tab2:
    st.header("Top Products")
    sum_order_items = create_sum_order_items_df(data_filtered)

    col1, col2 = st.columns(2)
    with col1:
        top_products = sum_order_items.head(10)
        fig, ax = plt.subplots()
        sns.barplot(x=top_products['quantity'], y=top_products['product_category_name_english'], palette='Greens_r', ax=ax)
        ax.set_title("Top 10 Product Categories")
        st.pyplot(fig)

    with col2:
        least_products = sum_order_items.tail(10)
        fig, ax = plt.subplots()
        sns.barplot(x=least_products['quantity'], y=least_products['product_category_name_english'], palette='Reds_r', ax=ax)
        ax.set_title("Bottom 10 Product Categories")
        st.pyplot(fig)

    # Product Sales Trends Over Time
    st.subheader("Product Category Sales Trends Over Time")
    category_trends = data_filtered.groupby(['order_date_month', 'product_category_name_english']).size().unstack().fillna(0)
    fig, ax = plt.subplots(figsize=(12, 8))
    for category in category_trends.columns[:10]:
        ax.plot(category_trends.index.astype(str), category_trends[category], label=category)
    ax.set_title('Product Category Sales Trends Over Time')
    ax.set_xlabel('Month')
    ax.set_ylabel('Number of Sales')
    ax.legend()
    ax.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(fig)

# Customer Insights Tab
with tab3:
    st.header("Customer Insights")
    state_counts = data_filtered['customer_state'].value_counts().head(10)
    fig, ax = plt.subplots()
    sns.barplot(x=state_counts.values, y=state_counts.index, palette='magma', ax=ax)
    ax.set_title("Top 10 States with the Most Customers")
    st.pyplot(fig)

st.caption('Copyright © Maharani Rizki F')
