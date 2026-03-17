import pandas as pd

df = pd.read_csv("medical_sales.csv")

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

print(df.head())