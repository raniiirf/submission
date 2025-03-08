import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load Data
@st.cache_data
def load_data():
    all_data = pd.read_csv("all_data.csv")
    all_data['order_date'] = pd.to_datetime(all_data['order_purchase_timestamp'])
    all_data['order_date_month'] = all_data['order_date'].dt.to_period('M')
    return all_data

data = load_data()

# Sidebar
st.sidebar.title("Dashboard")
st.sidebar.image("https://cubic.id/public/front/images/jurnals/eZqeYWHjdJBp7DfAnCneMAh5h5B6F75s4dRS0iUL.jpeg")

start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    [data['order_date'].min().date(), data['order_date'].max().date()]
)

if isinstance(start_date, tuple):
    start_date, end_date = start_date

start_date = pd.Timestamp(start_date)
end_date = pd.Timestamp(end_date)

data_filtered = data[(data['order_date'] >= start_date) & (data['order_date'] <= end_date)]

if data_filtered.empty:
    st.warning("No data available for the selected date range.")

# Helper Functions
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_date').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    daily_orders_df['total_sales'] = daily_orders_df['revenue']
    return daily_orders_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name_english").size().sort_values(ascending=False).reset_index(name='quantity')
    return sum_order_items_df

# Tabs
st.title("E-commerce Public Brazil Dashboard :sparkles:")

tab1, tab2, tab3 = st.tabs(["Sales Performance", "Top Products", "Customer Insights"])

with tab1:
    st.header("Sales Performance")
    st.subheader("Daily Orders")
    col1, col2, col3, col4 = st.columns(4)

    daily_orders = create_daily_orders_df(data_filtered)

    with col1:
        st.markdown("**Number of Daily Orders**")
        total_orders = daily_orders['order_count'].sum()
        st.metric("Total Orders", value=total_orders)

    with col2:
        st.markdown("**Total Sales**")
        total_sales = daily_orders['total_sales'].sum()
        st.metric("Total Sales", value=f"${total_sales:,.2f}")

    with col3:
        st.markdown("**Monthly Sales Performance**")
        monthly_sales = data_filtered.groupby(data_filtered['order_date'].dt.to_period('M'))['order_id'].count()
        fig, ax = plt.subplots()
        monthly_sales.plot(kind='line', marker='o', ax=ax)
        ax.set_title("Monthly Sales Performance")
        ax.set_xlabel("Month")
        ax.set_ylabel("Number of Orders")
        st.pyplot(fig)
    with col4:
        st.markdown("**Top 10 Cities with the Highest Sales**")
        city_orders = data_filtered.groupby("customer_city")['order_id'].count().nlargest(10)
        fig, ax = plt.subplots()
        sns.barplot(x=city_orders.values, y=city_orders.index, palette='Blues_r', ax=ax)
        ax.set_title("Top 10 Cities with the Highest Sales")
        st.pyplot(fig)

with tab2:
    st.header("Top Products")
    col1, col2 = st.columns(2)

    sum_order_items = create_sum_order_items_df(data_filtered)

    with col1:
        st.markdown("**Top 10 Product Categories with the Highest Sales**")
        top_products = sum_order_items.head(10)
        fig, ax = plt.subplots()
        sns.barplot(x=top_products['quantity'], y=top_products['product_category_name_english'], palette='Greens_r', ax=ax)
        ax.set_title("Top 10 Product Categories with the Highest Sales")
        st.pyplot(fig)

    with col2:
        st.markdown("**Bottom 10 Product Categories with the Lowest Sales**")
        least_products = sum_order_items.tail(10)
        fig, ax = plt.subplots()
        sns.barplot(x=least_products['quantity'], y=least_products['product_category_name_english'], palette='Reds_r', ax=ax)
        ax.set_title("Bottom 10 Product Categories with the Lowest Sales")
        st.pyplot(fig)

with tab3:
    st.header("Customer Insights")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Top 10 States with the Most Customers**")
        state_counts = data_filtered['customer_state'].value_counts().head(10)
        fig, ax = plt.subplots()
        sns.barplot(x=state_counts.values, y=state_counts.index, palette='magma', ax=ax)
        ax.set_title("Top 10 States with the Most Customers")
        st.pyplot(fig)

st.caption('Copyright © Maharani Rizki F')