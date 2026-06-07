from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import pandas as pd
import io
import sqlite3

app = FastAPI(title="Kadak WMS Backend")

# SYSTEM LOCK OPEN (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DUMMY ORDERS (Marketplace se aaye huye)
DUMMY_ORDERS = [
    {"order_no": "404-4816343-4371107", "channel": "Amazon", "status": "Allocated", "sku": "BJHND001"},
    {"order_no": "ORD-MEESHO-9921", "channel": "Meesho", "status": "Allocated", "sku": "JAPA-MALA"}
]

# ASALI DATABASE INIT (Tijori Setup)
def init_db():
    conn = sqlite3.connect("wms_tijori.db")
    cursor = conn.cursor()
    # Permanent table banana bundle mapping ke liye
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bundle_mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bundle_sku TEXT,
            child_sku TEXT,
            quantity INTEGER,
            rack_location TEXT
        )
    """)
    conn.commit()
    conn.close()

# Server chalu hote hi table automatic ban jayegi
init_db()

@app.get("/")
def home():
    return {"status": "Online", "message": "Bhai, Database Connect ho gaya hai!"}

@app.get("/api/orders")
def get_all_orders():
    return DUMMY_ORDERS

# 1. KADAK FEATURE: Bulk Excel Upload Se Asali Database Me Data Daalna
@app.post("/api/upload-mapping")
async def upload_bundle_mapping(file: UploadFile = File(...)):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Bhai ruko, sirf Excel (.xlsx) file hi chalegi!")
    
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        conn = sqlite3.connect("wms_tijori.db")
        cursor = conn.cursor()
        
        # Purana data clear karna taaki naya excel master fresh upload ho ske
        cursor.execute("DELETE FROM bundle_mappings")
        
        # Excel ki ek ek row ko database me save karna
        for index, row in df.iterrows():
            bundle_sku = str(row['Bundle_SKU']).strip()
            child_sku = str(row['Child_SKU']).strip()
            qty = int(row['Quantity'])
            rack = str(row.get('Rack_Location', 'General-Rack')).strip()
            
            cursor.execute("""
                INSERT INTO bundle_mappings (bundle_sku, child_sku, quantity, rack_location)
                VALUES (?, ?, ?, ?)
            """, (bundle_sku, child_sku, qty, rack))
            
        conn.commit()
        conn.close()
        
        return {"status": "Success", "message": f"Bhai, total {len(df)} rows database me safe save ho gayi!"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel columns sahi nahi hain: {str(e)}")

# 2. KADAK FEATURE: Database Se Dynamic Data Nikal Kar Picklist Split Karna
@app.get("/api/picklist-preview")
def preview_picklist():
    final_picklist = []
    
    conn = sqlite3.connect("wms_tijori.db")
    cursor = conn.cursor()
    
    for order in DUMMY_ORDERS:
        sku_naam = order["sku"]
        
        # Database me check karna ki kya yeh SKU ek bundle hai?
        cursor.execute("SELECT child_sku, quantity, rack_location FROM bundle_mappings WHERE bundle_sku = ?", (sku_naam,))
        components = cursor.fetchall()
        
        if components:
            # Agar bundle mil gaya database me, toh use split karke daalo
            for row in components:
                final_picklist.append({
                    "order_no": order["order_no"],
                    "sku": row[0],
                    "qty": row[1],
                    "rack": row[2],
                    "type": "Bundle Split Item"
                })
        else:
            # Varna normal entry rehne do
            final_picklist.append({
                "order_no": order["order_no"],
                "sku": order["sku"],
                "qty": 1,
                "rack": "General-Rack",
                "type": "Single Item"
            })
            
    conn.close()
    return {"items": final_picklist}