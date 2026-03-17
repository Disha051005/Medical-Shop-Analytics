import pandas as pd
import random
from datetime import datetime, timedelta

medicines = [
"Paracetamol","Crocin","Amoxicillin","Vitamin C","Azithromycin",
"Ibuprofen","Dolo","Cetirizine","Aspirin","Metformin",
"Pantoprazole","Omeprazole","Insulin","Atorvastatin","Losartan",
"Calcium Tablets","ORS","Cough Syrup","Antacid","Zinc Tablets",
"Vitamin B12","Diclofenac","Amoxyclav","Levocetirizine","Ranitidine"
]

data = []

for i in range(800):

    medicine = random.choice(medicines)
    quantity = random.randint(50,200)
    sold = random.randint(10,quantity)
    price = random.randint(5,60)

    purchase_date = datetime.now() - timedelta(days=random.randint(0,200))
    expiry_date = purchase_date + timedelta(days=random.randint(100,400))

    data.append([
        medicine,
        quantity,
        sold,
        price,
        purchase_date,
        expiry_date
    ])

df = pd.DataFrame(data, columns=[
"Medicine","Quantity","Sold","Price","Purchase_Date","Expiry_Date"
])

df.to_csv("medical_sales.csv", index=False)

print("Dataset generated successfully")