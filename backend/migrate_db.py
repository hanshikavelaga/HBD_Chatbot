import sqlite3
import os
import shutil
import hashlib
import uuid
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "google_map_data.db")
BACKUP_PATH = os.path.join(BASE_DIR, "google_map_data.db.bak")

def hash_password(password: str) -> str:
    # Secure salt-based password hashing using hashlib
    salt = "honeybee_digital_chatbot_salt_123"
    db_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return db_hash

def migrate():
    print("📦 Starting database analysis and schema migrations...")
    
    # 1. Back up database
    if os.path.exists(DB_PATH):
        print(f"  Creating database backup at: {BACKUP_PATH}")
        shutil.copyfile(DB_PATH, BACKUP_PATH)
    else:
        print("  Database file not found. Creating a new one...")
        
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Enable foreign keys
    cur.execute("PRAGMA foreign_keys = ON;")
    
    # 2. Create normalized users table
    print("  Creating 'users' table...")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        phone TEXT UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        status TEXT NOT NULL DEFAULT 'active',
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """)
    
    # 3. Create categories table
    print("  Creating 'categories' table...")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        parent_id INTEGER,
        icon TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
    );
    """)
    
    # 4. Create search_history table
    print("  Creating 'search_history' table...")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        search_query TEXT NOT NULL,
        resolved_city TEXT,
        resolved_category TEXT,
        timestamp TEXT NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    );
    """)
    
    # 5. Create audit_logs table
    print("  Creating 'audit_logs' table...")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        entity TEXT NOT NULL,
        entity_id INTEGER,
        ip_address TEXT,
        timestamp TEXT NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    );
    """)
    
    # 6. Add columns to existing tables if missing
    # Add 'owner_id' to g_map_master_table
    cur.execute("PRAGMA table_info(g_map_master_table);")
    columns = [col[1] for col in cur.fetchall()]
    if "owner_id" not in columns:
        print("  Adding 'owner_id' column to 'g_map_master_table'...")
        cur.execute("ALTER TABLE g_map_master_table ADD COLUMN owner_id INTEGER REFERENCES users(id) ON DELETE SET NULL;")
        
    # Add 'is_pinned' to chat_sessions
    cur.execute("PRAGMA table_info(chat_sessions);")
    columns_sessions = [col[1] for col in cur.fetchall()]
    if "is_pinned" not in columns_sessions:
        print("  Adding 'is_pinned' column to 'chat_sessions'...")
        cur.execute("ALTER TABLE chat_sessions ADD COLUMN is_pinned INTEGER DEFAULT 0;")
        
    # 7. Create database indexes for optimized fast search
    print("  Building query performance indexes...")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_gmap_city ON g_map_master_table (city);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_gmap_category ON g_map_master_table (business_category);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_gmap_score ON g_map_master_table (ratings, reviews_count);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages (session_id);")
    
    # 8. Migrate existing businesses to establish owner accounts
    print("  Backfilling owner user accounts from existing business emails & phones...")
    cur.execute("""
        SELECT global_business_id, email, phone_number, business_name 
        FROM g_map_master_table 
        WHERE (email IS NOT NULL AND email != '') 
           OR (phone_number IS NOT NULL AND phone_number != '')
    """)
    listings = cur.fetchall()
    
    default_pwd_hash = hash_password("password123")
    migrated_users = 0
    linked_listings = 0
    
    for biz_id, email, phone, name in listings:
        clean_email = email.strip() if email else None
        clean_phone = phone.strip() if phone else None
        
        if not clean_email and not clean_phone:
            continue
            
        # Find if user already exists
        user_id = None
        if clean_email:
            cur.execute("SELECT id FROM users WHERE email = ?", (clean_email,))
            row = cur.fetchone()
            if row:
                user_id = row[0]
        if not user_id and clean_phone:
            cur.execute("SELECT id FROM users WHERE phone = ?", (clean_phone,))
            row = cur.fetchone()
            if row:
                user_id = row[0]
                
        # Create user if not exists
        if not user_id:
            try:
                cur.execute("""
                    INSERT INTO users (email, phone, password_hash, role) 
                    VALUES (?, ?, ?, 'owner')
                """, (clean_email, clean_phone, default_pwd_hash))
                user_id = cur.lastrowid
                migrated_users += 1
            except sqlite3.IntegrityError:
                # Fallback if constraint triggers
                if clean_email:
                    cur.execute("SELECT id FROM users WHERE email = ?", (clean_email,))
                    r = cur.fetchone()
                    if r: user_id = r[0]
                if not user_id and clean_phone:
                    cur.execute("SELECT id FROM users WHERE phone = ?", (clean_phone,))
                    r = cur.fetchone()
                    if r: user_id = r[0]
                    
        # Update owner_id in listing
        if user_id:
            cur.execute("UPDATE g_map_master_table SET owner_id = ? WHERE global_business_id = ?", (user_id, biz_id))
            linked_listings += 1
            
    print(f"  Migrated {migrated_users} unique owners and linked {linked_listings} business listings.")
    
    # 9. Build parent-child category tree dynamically from database listings
    print("  Generating category tree dynamically...")
    
    # Parent Categories Map (Keyword -> Parent Category Name)
    parent_mapping = {
        "gym": "Gym & Fitness",
        "fitness": "Gym & Fitness",
        "sports": "Gym & Fitness",
        "restaurant": "Food & Dining",
        "cafe": "Food & Dining",
        "bakery": "Food & Dining",
        "hotel": "Food & Dining",
        "food": "Food & Dining",
        "salon": "Beauty & Spas",
        "beauty": "Beauty & Spas",
        "spa": "Beauty & Spas",
        "hospital": "Healthcare",
        "clinic": "Healthcare",
        "pharmacy": "Healthcare",
        "doctor": "Healthcare",
        "dentist": "Healthcare",
        "school": "Education",
        "college": "Education",
        "academy": "Education",
        "education": "Education",
        "shop": "Shopping",
        "grocery": "Shopping",
        "clothing": "Shopping",
        "boutique": "Shopping",
        "jewellery": "Shopping",
        "electronics": "Shopping",
        "furniture": "Shopping",
        "hardware": "Shopping",
        "automobile": "Automobile",
        "car": "Automobile",
        "bike": "Automobile",
        "garage": "Automobile",
        "advocate": "Professional Services",
        "lawyer": "Professional Services",
        "software": "Professional Services",
        "it services": "Professional Services",
        "advertising": "Professional Services",
        "laundry": "Professional Services"
    }
    
    # Standard Icons map for categories
    icons_map = {
        "Gym & Fitness": "Dumbbell",
        "Food & Dining": "Utensils",
        "Beauty & Spas": "Sparkles",
        "Healthcare": "HeartPulse",
        "Education": "GraduationCap",
        "Shopping": "ShoppingBag",
        "Automobile": "Car",
        "Professional Services": "Briefcase",
        "Other Services": "Tag"
    }
    
    # Load all distinct categories
    cur.execute("SELECT DISTINCT LOWER(business_category) FROM g_map_master_table WHERE business_category IS NOT NULL AND business_category != ''")
    db_categories = [r[0] for r in cur.fetchall()]
    
    # Ensure parents exist
    parent_ids = {}
    for parent_name in set(parent_mapping.values()):
        try:
            cur.execute("INSERT OR IGNORE INTO categories (name, icon) VALUES (?, ?)", (parent_name, icons_map.get(parent_name, "Tag")))
            cur.execute("SELECT id FROM categories WHERE name = ?", (parent_name,))
            parent_ids[parent_name] = cur.fetchone()[0]
        except Exception as err:
            print(f"    Failed to insert parent category {parent_name}: {err}")
            
    # Add 'Other Services' parent fallback
    cur.execute("INSERT OR IGNORE INTO categories (name, icon) VALUES (?, ?)", ("Other Services", "Tag"))
    cur.execute("SELECT id FROM categories WHERE name = ?", ("Other Services",))
    parent_ids["Other Services"] = cur.fetchone()[0]
    
    # Add child categories
    seeded_children = 0
    for child in db_categories:
        child_title = child.title()
        # Skip if same as parent
        if child_title in parent_ids:
            continue
            
        # Determine parent
        parent_name = "Other Services"
        for kw, p_name in parent_mapping.items():
            if kw in child:
                parent_name = p_name
                break
                
        parent_id = parent_ids.get(parent_name)
        try:
            cur.execute("INSERT OR IGNORE INTO categories (name, parent_id, icon) VALUES (?, ?, ?)", (child_title, parent_id, "Tag"))
            seeded_children += 1
        except Exception as err:
            print(f"    Failed to insert child category {child_title}: {err}")
            
    print(f"  Successfully seeded category hierarchy tree ({len(parent_ids)} parents, {seeded_children} child subcategories).")
    
    conn.commit()
    conn.close()
    print("✅ Database migration and structural enhancements complete!")

if __name__ == "__main__":
    migrate()
