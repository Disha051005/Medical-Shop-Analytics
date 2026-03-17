import sqlite3
import pandas as pd

df = pd.read_csv("medical_sales.csv")

conn = sqlite3.connect("medical.db")

df.to_sql("sales", conn, if_exists="replace", index=False)

print("Database created successfully")