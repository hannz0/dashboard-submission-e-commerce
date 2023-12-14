import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set_theme(context="talk")
sns.set_style("whitegrid", {'axes.edgecolor': '.6','xtick.bottom': True,'ytick.left': True})

# Semua function yang dibutuhkan dalam pembuatan dataframe sesuai visualisasinya

def create_product_sales_df(df):
    product_sales_df = df.groupby("product_category_name_english").order_id.count().sort_values(ascending=False).reset_index()
    product_sales_df.rename(columns={
        "product_category_name_english": "category",
        "order_id": "qty"
        }, inplace=True)
    return product_sales_df

def create_bycity_df(df):
    bycity_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    bycity_df.rename(columns={
        "customer_id": "total_customer"
        }, inplace=True)
    return bycity_df

def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "total_customer"
        }, inplace=True)

    return bystate_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",
        "order_id": "nunique",
        "price": "sum"
        })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    # menghitung kapan terakhir pelanggan melakukan transaksi (hari)
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df

# load dataset
df = pd.read_csv("main_data.csv")

datetime_columns = ['order_purchase_timestamp',
                    'order_approved_at',
                    'order_delivered_carrier_date',
                    'order_delivered_customer_date',
                    'order_estimated_delivery_date',
                    'shipping_limit_date']

for col in datetime_columns:
    df[col] = pd.to_datetime(df[col])

df.sort_values(by="order_purchase_timestamp", inplace=True)
df.reset_index(inplace=True)

min_date = df["order_purchase_timestamp"].min()
max_date = df["order_purchase_timestamp"].max()

with st.sidebar:
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
# dataset ini berdasarkan pilihan rentang waktu/tanggal yang telah dipilih
main_df = df[(df["order_purchase_timestamp"] >= str(start_date)) &
                (df["order_purchase_timestamp"] <= str(end_date))]

# menyiapkan beberapa dataset dari function yang telah dibuat
product_sales_df = create_product_sales_df(main_df)
bycity_df = create_bycity_df(main_df)
bystate_df = create_bystate_df(main_df)
rfm_df = create_rfm_df(main_df)

st.header('E-Commerce Public Dashboard 🏬')

# Product performance
st.subheader("Most & Fewest Purchased Product")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(38, 15))
best_clr = ["#007B5A", "#6CC4A1", "#6CC4A1", "#6CC4A1", "#6CC4A1", "#6CC4A1", "#6CC4A1", "#6CC4A1", "#6CC4A1", "#6CC4A1"]
fewest_clr = ["#FF6D60", "#FFBA92", "#FFBA92", "#FFBA92", "#FFBA92", "#FFBA92", "#FFBA92", "#FFBA92", "#FFBA92", "#FFBA92"]

sns.barplot(x="qty", y="category", data=product_sales_df.head(5), palette=best_clr, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=40)
ax[0].set_title("Most Purchased Products", loc="center", fontsize=70, pad=30)
ax[0].tick_params(axis='x', labelsize=35)
ax[0].tick_params(axis ='y', labelsize=40)

sns.barplot(x="qty", y="category", data=product_sales_df.sort_values(by="qty", ascending=True).head(5), palette=fewest_clr, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=40)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Fewest Purchased Products", loc="center", fontsize=70, pad=30)
ax[1].tick_params(axis='x', labelsize=35)
ax[1].tick_params(axis='y', labelsize=40)

st.pyplot(fig)

# Customer Demographic
st.subheader("Customer Demographics")
fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(26, 24))
sns.barplot(
    x="total_customer",
    y="customer_city",
    data=bycity_df.sort_values(by="total_customer", ascending=False).head(10),
    palette=best_clr,
    ax=ax[0]
    )
ax[0].set_title("Customer by City", loc="center", fontsize=50, pad=20)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].tick_params(axis='x', labelsize=30)
ax[0].tick_params(axis='y', labelsize=30)

sns.barplot(
    x="total_customer",
    y="customer_state",
    data=bystate_df.sort_values(by="total_customer", ascending=False).head(10),
    palette=best_clr,
    ax=ax[1]
    )
ax[1].set_title("Customer by States", loc="center", fontsize=50, pad=20)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].tick_params(axis='x', labelsize=30)
ax[1].tick_params(axis='y', labelsize=30)

st.pyplot(fig)

# Based on RFM Analysis
st.subheader("Customer Evaluation Based on RFM Analysis")
col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "BRL", locale='pt_BR')
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#6CC4A1", "#6CC4A1", "#6CC4A1", "#6CC4A1", "#6CC4A1"]

rfm_recency = rfm_df.sort_values(by="recency", ascending=True).head(5).copy()
rfm_recency['customer_id'] = rfm_recency.index
rfm_frequency = rfm_df.sort_values(by="frequency", ascending=False).head(5).copy()
rfm_frequency['customer_id'] = rfm_frequency.index
rfm_monetary = rfm_df.sort_values(by="monetary", ascending=False).head(5).copy()
rfm_monetary['customer_id'] = rfm_monetary.index

sns.barplot(y="recency", x="customer_id", data=rfm_recency, palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=40)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50, pad=30)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(y="frequency", x="customer_id", data=rfm_frequency, palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=40)
ax[1].set_title("By Frequency", loc="center", fontsize=50, pad=30)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=30)

sns.barplot(y="monetary", x="customer_id", data=rfm_monetary, palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=40)
ax[2].set_title("By Monetary", loc="center", fontsize=50, pad=30)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

st.caption('Copyright © Hann')