from fastapi import FastAPI, HTTPException, UploadFile, File
from typing import List, Dict
from datetime import datetime
import pandas as pd
import io

app = FastAPI(title="Kadak WMS Backend")

# 1. Fake Orders Data
DUMMY_ORDERS = [
    {"order_no": "404-4816343-4371107", "channel": "Amazon", "status": "Allocated", "sku": "BJHND001"},
    {"order_no": "ORD-MEESHO-9921", "channel": "Meesho", "status": "Allocated", "sku": "JAPA-MALA"}
]

# 2. Dynamic Bundle Mapping (Ab yeh khaali hai, client excel se bharega!)
BUNDLE_MAPPING = {}

TRACK_PICKLISTS = {}
picklist_counter = 1

@app.get("/")
def home():
    return {"status": "Online", "message": "Bhai, WMS server ekdam mast chal raha hai!"}

@app.get("/api/orders")
def get_all_orders():
    return DUMMY_ORDERS

# 3. KADAK FEATURE: Client Side Bulk Excel Upload for Bundle Mapping
@app.post("/api/upload-mapping")
async def upload_bundle_mapping(file: UploadFile = File(...)):
    global BUNDLE_MAPPING
    
    # Check karna ki file sirf Excel (.xlsx) hi ho
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Bhai ruko, sirf Excel (.xlsx) file hi upload karo!")
    
    try:
        # Excel file ko read karna binary format se
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Pehle se agar koi mapping hai toh use fresh karne ke liye clear kar sakte hain
        new_mapping = {}
        
        # Excel ki har ek row ko check karna aur system me dalna
        for index, row in df.iterrows():
            parent_sku = str(row['Bundle_SKU']).strip()
            child_sku = str(row['Child_SKU']).strip()
            qty = int(row['Quantity'])
            rack = str(row.get('Rack_Location', 'General-Rack')).strip()
            
            # Agar bundle naya hai, toh uski list banao
            if parent_sku not in new_mapping:
                new_mapping[parent_sku] = []
                
            new_mapping[parent_sku].append({
                "child_sku": child_sku,
                "qty": qty,
                "rack_location": rack
            })
            
        # Hamari main dynamic data tijori ko update kar dena
        BUNDLE_MAPPING = new_mapping
        
        return {
            "status": "Success", 
            "message": f"Bhai, total {len(df)} rows check ho gayi aur bundle mapping live update ho gayi!"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel processing me kuch galti hui: {str(e)}")

# 4. Picklist Generation (Jo ab dynamic bundle mapping use karega)
@app.get("/api/picklist-preview")
def preview_picklist():
    final_picklist = []
    for order in DUMMY_ORDERS:
        sku_naam = order["sku"]
        if sku_naam in BUNDLE_MAPPING:
            for item in BUNDLE_MAPPING[sku_naam]:
                final_picklist.append({
                    "order_no": order["order_no"],
                    "sku": item["child_sku"],
                    "qty": item["qty"],
                    "rack": item["rack_location"],
                    "type": "Bundle Split Item"
                })
        else:
            final_picklist.append({
                "order_no": order["order_no"],
                "sku": order["sku"],
                "qty": 1,
                "rack": "General-Rack",
                "type": "Single Item"
            })
    return {"items": final_picklist}