from fastapi import FastAPI
from typing import List, Dict

app = FastAPI(title="Kadak WMS Backend")

# 1. Fake Orders Data (Jo marketplaces se aata hai)
DUMMY_ORDERS = [
    {
        "order_no": "404-4816343-4371107",
        "channel": "Amazon",
        "order_type": "Prepaid",
        "status": "Allocated",
        "customer_name": "Pawan Kumar",
        "sku": "BJHND001"  # Yeh tumhara main Bundle SKU hai
    },
    {
        "order_no": "ORD-MEESHO-9921",
        "channel": "Meesho",
        "order_type": "COD",
        "status": "New",
        "customer_name": "Sanjeev Sharma",
        "sku": "JAPA-MALA"  # Yeh single SKU hai
    }
]

# 2. Bundle Master Mapping (Tijori jise baad me client excel se upload karega)
BUNDLE_MAPPING = {
    "BJHND001": [
        {"child_sku": "BG-HINDI", "qty": 1, "rack_location": "Rack-A1"},
        {"child_sku": "JAPA-MALA", "qty": 1, "rack_location": "Rack-B4"}
    ]
}

@app.get("/")
def home():
    return {"status": "Online", "message": "Bhai, WMS server ekdam mast chal raha hai!"}

@app.get("/api/orders")
def get_all_orders():
    return DUMMY_ORDERS

# 3. KADAK FEATURE: Picklist Generation with Auto SKU Splitting
@app.get("/api/picklist")
def generate_picklist():
    final_picklist = []
    
    for order in DUMMY_ORDERS:
        sku_naam = order["sku"]
        
        # Agar SKU bundle master mapping me maujood hai (Jaise BJHND001)
        if sku_naam in BUNDLE_MAPPING:
            # Bundle ko todo aur uske andar ke saare products nikaalo
            components = BUNDLE_MAPPING[sku_naam]
            for item in components:
                final_picklist.append({
                    "order_no": order["order_no"],
                    "customer_name": order["customer_name"],
                    "channel": order["channel"],
                    "final_packing_sku": item["child_sku"], # Split ho gaya!
                    "quantity": item["qty"],
                    "rack_location": item["rack_location"]   # Warehouse boy ko rasta dikhane ke liye
                })
        else:
            # Agar normal single product hai, toh bina split kiye direct picklist me daalo
            final_picklist.append({
                "order_no": order["order_no"],
                "customer_name": order["customer_name"],
                "channel": order["channel"],
                "final_packing_sku": order["sku"],
                "quantity": 1,
                "rack_location": "General-Rack"
            })
            
    return {"status": "Success", "items_to_pick": final_picklist}