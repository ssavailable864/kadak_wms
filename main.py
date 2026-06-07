from fastapi import FastAPI
from typing import List, Dict

app = FastAPI(title="Kadak WMS Backend")

# Yeh hamara temporary database hai (Tijori), jisme video ke hisab se data dala hai
DUMMY_ORDERS = [
    {
        "order_no": "404-4816343-4371107",
        "channel": "Amazon",
        "order_type": "Prepaid",
        "status": "Allocated",
        "customer_name": "Pawan Kumar",
        "sku": "BJHND001" # Tera Bundle SKU
    },
    {
        "order_no": "ORD-MEESHO-9921",
        "channel": "Meesho",
        "order_type": "COD",
        "status": "New",
        "customer_name": "Sanjeev Sharma",
        "sku": "JAPA-MALA"
    },
    {
        "order_no": "ORD-FLIPKART-8832",
        "channel": "Flipkart",
        "order_type": "Prepaid",
        "status": "Packed",
        "customer_name": "Rajesh Gupta",
        "sku": "BG-HINDI"
    }
]

# 1. Main Home Route (Check karne ke liye ki server chalu hai)
@app.get("/")
def home():
    return {"status": "Online", "message": "Bhai, WMS server ekdam mast chal raha hai!"}

# 2. Orders Route (Dashboard ke saare orders nikaalne ke liye)
@app.get("/api/orders")
def get_all_orders():
    return DUMMY_ORDERS