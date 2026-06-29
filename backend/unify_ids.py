import sqlite3
import csv
import os

CSV_PATH = 'backend/g_map_master_table_sample.csv'
DB_PATH = 'backend/google_map_data.db'

def unify_ids():
    print("📋 Checking IDs for all businesses...")
    
    # 1. READ CSV
    businesses = []
    if not os.path.exists(CSV_PATH):
        print("❌ CSV not found.")
        return
        
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames
        for index, row in enumerate(reader, start=1):
            # Enforce sequential ID starting from 1
            row['id'] = str(index)
            businesses.append(row)
            
    # 2. WRITE CLEAN CSV
    with open(CSV_PATH, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(businesses)
    print(f"✅ CSV updated with {len(businesses)} unique sequential IDs.")

    # 3. UPDATE DB
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # We'll drop and recreate the listings table to be 100% clean and matching CSV
        cur.execute("DROP TABLE IF EXISTS google_maps_listings")
        cur.execute("""
        CREATE TABLE google_maps_listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address TEXT,
            website TEXT,
            phone_number TEXT,
            reviews_count INTEGER,
            reviews_average REAL,
            category TEXT,
            subcategory TEXT,
            city TEXT,
            state TEXT,
            area TEXT,
            created_at TEXT
        )
        """)
        
        for b in businesses:
            cur.execute("""
            INSERT INTO google_maps_listings (
                id, name, address, website, phone_number, reviews_count, reviews_average, category, subcategory, city, state, area, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                int(b['id']), b['name'], b['address'], b['website'], b['phone_number'],
                int(b.get('reviews_count') or 0), float(b.get('reviews_avg') or 0.0),
                b['category'], b['subcategory'], b['city'], b['state'], b['area'], b.get('created_at') or ""
            ))
            
        conn.commit()
        conn.close()
        print("✅ Database successfully synced with clean CSV IDs.")

if __name__ == "__main__":
    unify_ids()
