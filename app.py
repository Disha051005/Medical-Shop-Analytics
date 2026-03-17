import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Medical Shop Analytics", layout="wide")

# ------------------ BEAUTIFUL STYLE ------------------
st.markdown("""
<style>

.stApp{
background: linear-gradient(to right,#e3f2fd,#ffffff);
}

h1{
text-align:center;
color:#d32f2f;
}

.sidebar .sidebar-content{
background-color:#f5f5f5;
}

</style>
""", unsafe_allow_html=True)

st.title("💊 Medical Shop Sales & Expiry Risk Analytics")

# ------------------ DATABASE ------------------
conn = sqlite3.connect("medical.db")
df = pd.read_sql("SELECT * FROM sales", conn)

df["Expiry_Date"] = pd.to_datetime(df["Expiry_Date"])

today = pd.Timestamp.today()

df["Days_Left"] = (df["Expiry_Date"] - today).dt.days

def expiry_risk(days):

    if days < 30:
        return "High Risk"
    elif days < 90:
        return "Medium Risk"
    else:
        return "Low Risk"

df["Expiry_Risk"] = df["Days_Left"].apply(expiry_risk)

df["Unsold"] = df["Quantity"] - df["Sold"]

df["Potential_Loss"] = df["Unsold"] * df["Price"]

# ------------------ SIDEBAR ------------------
menu = st.sidebar.selectbox(
"Navigation",
["Dashboard","Sales Analysis","Expiry Analysis","Search Medicine","Database"]
)

# ------------------ DASHBOARD ------------------
if menu == "Dashboard":

    st.subheader("📊 Overall Statistics")

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("💊 Medicines", df["Medicine"].nunique())

    col2.metric("📦 Total Stock", int(df["Quantity"].sum()))

    col3.metric("🛒 Total Sold", int(df["Sold"].sum()))

    col4.metric("💰 Revenue", int((df["Sold"]*df["Price"]).sum()))

    st.divider()

    st.subheader("🏆 Top 10 Selling Medicines")

    top = df.groupby("Medicine")["Sold"].sum().sort_values(ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(10,5))

    sns.barplot(
        x=top.values,
        y=top.index,
        palette="viridis",
        ax=ax
    )

    ax.set_xlabel("Units Sold")

    st.pyplot(fig)

# ------------------ SALES ANALYSIS ------------------
elif menu == "Sales Analysis":

    st.subheader("📈 Medicine Sales Analysis")

    selected = st.multiselect(
        "Select Medicines",
        df["Medicine"].unique(),
        default=df["Medicine"].unique()
    )

    filtered = df[df["Medicine"].isin(selected)]

    sales = filtered.groupby("Medicine")["Sold"].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(12,6))

    sns.barplot(
        x=sales.index,
        y=sales.values,
        palette="Spectral",
        ax=ax
    )

    plt.xticks(rotation=70)

    st.pyplot(fig)

    st.subheader("🏆 Top 10 Sales Distribution")

    top10 = sales.head(10)

    fig2, ax2 = plt.subplots()

    ax2.pie(
        top10.values,
        labels=top10.index,
        autopct="%1.1f%%",
        startangle=90
    )

    ax2.axis("equal")

    st.pyplot(fig2)

# ------------------ EXPIRY ANALYSIS ------------------
elif menu == "Expiry Analysis":

    st.subheader("⚠ Medicines Expiring Soon")

    expiry_alert = df[df["Days_Left"] < 30]

    st.dataframe(expiry_alert)

    st.subheader("💰 Potential Expiry Loss")

    loss = df["Potential_Loss"].sum()

    st.metric("Total Loss", int(loss))

    st.subheader("Expiry Risk Distribution")

    risk = df["Expiry_Risk"].value_counts()

    fig3, ax3 = plt.subplots()

    ax3.pie(
        risk.values,
        labels=risk.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=["red","orange","green"]
    )

    st.pyplot(fig3)

# ------------------ SEARCH ------------------
elif menu == "Search Medicine":

    st.subheader("🔍 Search Medicine")

    search = st.text_input("Enter Medicine Name")

    result = df[df["Medicine"].str.contains(search, case=False)]

    st.dataframe(result)

# ------------------ DATABASE ------------------
elif menu == "Database":

    st.subheader("📋 Complete Dataset")

    st.dataframe(df)