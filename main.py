from fastapi import FastAPI, HTTPException
from typing import List, Dict
from datetime import datetime

app = FastAPI(title="Kadak WMS Backend")

# 1. Fake Orders Data
DUMMY_ORDERS = [
    {"order_no": "404-4816343-4371107", "channel": "Amazon", "status": "Allocated", "sku": "BJHND001"},
    {"order_no": "ORD-MEESHO-9921", "channel": "Meesho", "status": "Allocated", "sku": "JAPA-MALA"},
    {"order_no": "ORD-FLIPKART-8832", "channel": "Flipkart", "status": "Allocated", "sku": "BG-HINDI"}
]

BUNDLE_MAPPING = {
    "BJHND001": [
        {"child_sku": "BG-HINDI", "qty": 1, "rack_location": "Rack-A1"},
        {"child_sku": "JAPA-MALA", "qty": 1, "rack_location": "Rack-B4"}
    ]
}

# 2. Master Picklist Storage (Hamari Picklist ki Tijori)
TRACK_PICKLISTS = {}
picklist_counter = 1

@app.get("/")
def home():
    return {"status": "Online", "message": "Bhai, WMS server ekdam mast chal raha hai!"}

# 3. KADAK FEATURE: Generate Unique Picklist No & Assign Picker
@app.post("/api/create-picklist")
def create_picklist(picker_name: str):
    global picklist_counter
    
    # Unique Picklist No Generate Karna
    picklist_no = f"PK-{datetime.now().year}-00{picklist_counter}"
    picklist_counter += 1
    
    items_to_pick = []
    
    # Saare allocated orders ko is picklist me daalna aur split karna
    for order in DUMMY_ORDERS:
        sku_naam = order["sku"]
        if sku_naam in BUNDLE_MAPPING:
            for item in BUNDLE_MAPPING[sku_naam]:
                items_to_pick.append({
                    "order_no": order["order_no"],
                    "sku": item["child_sku"],
                    "qty": item["qty"],
                    "rack": item["rack_location"],
                    "item_status": "Pending" # Shuruat me pending rahega
                })
        else:
            items_to_pick.append({
                "order_no": order["order_no"],
                "sku": order["sku"],
                "qty": 1,
                "rack": "General-Rack",
                "item_status": "Pending"
            })
            
    # Picklist ka master record save karna
    TRACK_PICKLISTS[picklist_no] = {
        "picklist_no": picklist_no,
        "assigned_to": picker_name,          # Kisko assign kiya (e.g., Ramesh)
        "total_items": len(items_to_pick),
        "picked_count": 0,                   # Kitna pick hua hai
        "status": "In-Progress",             # Status: In-Progress, Picked
        "items": items_to_pick
    }
    
    return {"message": f"Bhai, unique {picklist_no} generate ho gayi!", "data": TRACK_PICKLISTS[picklist_no]}

# 4. KADAK FEATURE: Strict Rule - Only Picked items can be Packed
@app.post("/api/pack-order")
def pack_order(picklist_no: str, order_no: str):
    # Check karo ki picklist exist karti hai ya nahi
    if picklist_no not in TRACK_PICKLISTS:
        raise HTTPException(status_code=404, detail="Bhai, yeh picklist number galat hai!")
        
    picklist_data = TRACK_PICKLISTS[picklist_no]
    
    # STRICT RULE CHECK: Agar picklist status 'Picked' nahi hai, toh packing block!
    if picklist_data["status"] != "Picked":
        raise HTTPException(
            status_code=400, 
            detail=f"Bhai Ruko! Picklist {picklist_no} abhi fully Picked nahi hui hai. Part wale ko pack nahi kar sakte!"
        )
        
    return {"status": "Success", "message": f"Order {order_no} successfully Packed ho gaya!"}