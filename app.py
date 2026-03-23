import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Medical Analytics", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right,#e3f2fd,#ffffff);
}
h1 {
    color:#d32f2f;
    text-align:center;
}
</style>
""", unsafe_allow_html=True)

st.title("💊 Medical Shop Sales & Expiry Risk Analytics")

# ---------------- DATABASE ----------------
conn = sqlite3.connect("medical.db")
df = pd.read_sql("SELECT * FROM sales", conn)

# ---------------- PREPROCESS ----------------
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

# ⭐ BEST RESTOCK LOGIC (PERCENTAGE BASED)
df["Stock_Percentage"] = (df["Unsold"] / df["Quantity"]) * 100

# ---------------- SIDEBAR ----------------
menu = st.sidebar.selectbox(
    "Navigation",
    ["Dashboard","Sales Analysis","Expiry Analysis",
     "Prediction","Recommendations","Database"]
)

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":

    st.subheader("📊 Overview")

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("💊 Medicines", df["Medicine"].nunique())
    col2.metric("📦 Stock", int(df["Quantity"].sum()))
    col3.metric("🛒 Sold", int(df["Sold"].sum()))
    col4.metric("💰 Revenue", int((df["Sold"]*df["Price"]).sum()))

    st.divider()

    st.subheader("🏆 Top Selling Medicines")

    top = df.groupby("Medicine")["Sold"].sum().sort_values(ascending=False).head(10)

    fig, ax = plt.subplots()
    sns.barplot(x=top.values, y=top.index, palette="viridis", ax=ax)
    st.pyplot(fig)

# ---------------- SALES ANALYSIS ----------------
elif menu == "Sales Analysis":

    st.subheader("📈 Sales Analysis")

    sales = df.groupby("Medicine")["Sold"].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(10,5))
    sns.barplot(x=sales.index, y=sales.values, palette="Spectral", ax=ax)
    plt.xticks(rotation=70)
    st.pyplot(fig)

    st.subheader("🏆 Top 10 Distribution")

    top10 = sales.head(10)

    fig2, ax2 = plt.subplots()
    ax2.pie(top10.values, labels=top10.index, autopct="%1.1f%%")
    st.pyplot(fig2)

# ---------------- EXPIRY ANALYSIS ----------------
elif menu == "Expiry Analysis":

    st.subheader("⚠ Expiring Soon")

    expiring = df[df["Days_Left"] < 30]
    st.dataframe(expiring)

    st.subheader("💰 Total Loss")

    loss = df["Potential_Loss"].sum()
    st.metric("Loss", int(loss))

    st.subheader("💰 Top Loss Medicines")

    top_loss = df.sort_values(by="Potential_Loss", ascending=False).head(5)
    st.dataframe(top_loss[["Medicine","Potential_Loss","Days_Left"]])

    st.subheader("Expiry Risk Distribution")

    risk = df["Expiry_Risk"].value_counts()

    fig, ax = plt.subplots()
    ax.pie(risk.values, labels=risk.index, autopct="%1.1f%%",
           colors=["red","orange","green"])
    st.pyplot(fig)

# ---------------- PREDICTION ----------------
elif menu == "Prediction":

    st.subheader("🤖 Sales Prediction (ML Model)")

    X = df[["Quantity","Price"]]
    y = df["Sold"]

    model = LinearRegression()
    model.fit(X,y)

    qty = st.number_input("Enter Quantity", 10, 500)
    price = st.number_input("Enter Price", 1, 100)

    if st.button("Predict"):
        pred = model.predict([[qty,price]])
        st.success(f"Predicted Sales: {int(pred[0])}")

# ---------------- RECOMMENDATIONS ----------------
elif menu == "Recommendations":

    st.subheader("💡 Smart Recommendations")

    # Expiry Risk
    high_risk = df[df["Expiry_Risk"]=="High Risk"]

    if not high_risk.empty:
        st.warning("⚠ Discount these medicines:")
        st.dataframe(high_risk[["Medicine","Days_Left","Potential_Loss"]])
    else:
        st.success("No high-risk medicines")

    # ⭐ BEST RESTOCK SYSTEM
    st.subheader("📦 Restock Needed (Smart System)")

    restock = df[df["Stock_Percentage"] < 20]

    if restock.empty:
        st.success("No restock needed")
    else:
        st.dataframe(restock[[
            "Medicine",
            "Quantity",
            "Unsold",
            "Stock_Percentage"
        ]])

# ---------------- DATABASE ----------------
elif menu == "Database":

    st.subheader("📋 Full Dataset")

    st.dataframe(df)