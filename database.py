import sqlite3
import os
from datetime import datetime

DB_NAME = "stylesphere.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the SQLite database schema."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Wardrobe table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wardrobe (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_path TEXT,
        category TEXT NOT NULL,
        colors TEXT NOT NULL,
        pattern TEXT,
        sleeve_type TEXT,
        season_suitability TEXT,
        fabric TEXT,
        brand TEXT,
        purchase_date TEXT,
        price REAL DEFAULT 0.0,
        wear_count INTEGER DEFAULT 0,
        last_worn_date TEXT,
        tags TEXT,
        notes TEXT
    )
    """)
    
    # 2. Usage history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usage_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wardrobe_id INTEGER NOT NULL,
        date_worn TEXT NOT NULL,
        occasion TEXT NOT NULL,
        rating INTEGER DEFAULT 0,
        feedback TEXT,
        FOREIGN KEY(wardrobe_id) REFERENCES wardrobe(id) ON DELETE CASCADE
    )
    """)
    
    # 3. Outfits table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS outfits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        items TEXT NOT NULL, -- Comma-separated wardrobe IDs e.g., "1,2,3"
        occasion TEXT NOT NULL,
        date_recommended TEXT NOT NULL,
        rating INTEGER DEFAULT 0,
        is_favorite INTEGER DEFAULT 0
    )
    """)
    
    # 4. Preferences table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS preferences (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """)
    
    # 5. Wishlist table (Shopping advisor wishlist)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wishlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_path TEXT,
        category TEXT NOT NULL,
        colors TEXT NOT NULL,
        pattern TEXT,
        sleeve_type TEXT,
        season_suitability TEXT,
        fabric TEXT,
        price REAL DEFAULT 0.0,
        estimated_wear_count INTEGER DEFAULT 10,
        is_purchased INTEGER DEFAULT 0
    )
    """)
    
    conn.commit()
    conn.close()

# ----------------- WARDROBE CRUD -----------------

def add_clothing_item(category, colors, pattern=None, sleeve_type=None, season_suitability=None, 
                      fabric=None, brand=None, purchase_date=None, price=0.0, tags=None, notes=None, image_path=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO wardrobe (category, colors, pattern, sleeve_type, season_suitability, fabric, brand, purchase_date, price, tags, notes, image_path)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (category, colors, pattern, sleeve_type, season_suitability, fabric, brand, purchase_date, price, tags, notes, image_path))
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    return item_id

def get_all_clothing_items():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM wardrobe ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_clothing_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM wardrobe WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_clothing_by_category(category):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM wardrobe WHERE category = ?", (category,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_clothing_item(item_id, **kwargs):
    if not kwargs:
        return
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "UPDATE wardrobe SET "
    params = []
    for k, v in kwargs.items():
        query += f"{k} = ?, "
        params.append(v)
    query = query.rstrip(", ") + " WHERE id = ?"
    params.append(item_id)
    
    cursor.execute(query, tuple(params))
    conn.commit()
    conn.close()

def delete_clothing_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM wardrobe WHERE id = ?", (item_id,))
    cursor.execute("DELETE FROM usage_history WHERE wardrobe_id = ?", (item_id,))
    conn.commit()
    conn.close()

# ----------------- USAGE LOGS -----------------

def log_clothing_wear(item_id, occasion, date_worn=None, rating=0, feedback=None):
    if not date_worn:
        date_worn = datetime.now().strftime("%Y-%m-%d")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Add usage entry
    cursor.execute("""
    INSERT INTO usage_history (wardrobe_id, date_worn, occasion, rating, feedback)
    VALUES (?, ?, ?, ?, ?)
    """, (item_id, date_worn, occasion, rating, feedback))
    
    # Increment wear count & update last worn date in wardrobe
    cursor.execute("""
    UPDATE wardrobe 
    SET wear_count = wear_count + 1, last_worn_date = ?
    WHERE id = ?
    """, (date_worn, item_id))
    
    conn.commit()
    conn.close()

def get_usage_history():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT uh.*, w.category, w.colors, w.brand, w.image_path 
    FROM usage_history uh 
    JOIN wardrobe w ON uh.wardrobe_id = w.id
    ORDER BY uh.date_worn DESC, uh.id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ----------------- OUTFITS -----------------

def save_recommended_outfit(name, description, items, occasion, rating=0, is_favorite=0):
    conn = get_db_connection()
    cursor = conn.cursor()
    date_recommended = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
    INSERT INTO outfits (name, description, items, occasion, date_recommended, rating, is_favorite)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, description, items, occasion, date_recommended, rating, is_favorite))
    conn.commit()
    outfit_id = cursor.lastrowid
    conn.close()
    return outfit_id

def get_outfits(favorites_only=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    if favorites_only:
        cursor.execute("SELECT * FROM outfits WHERE is_favorite = 1 ORDER BY id DESC")
    else:
        cursor.execute("SELECT * FROM outfits ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_outfit_favorite(outfit_id, is_favorite):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE outfits SET is_favorite = ? WHERE id = ?", (is_favorite, outfit_id))
    conn.commit()
    conn.close()

def rate_outfit(outfit_id, rating):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE outfits SET rating = ? WHERE id = ?", (rating, outfit_id))
    conn.commit()
    conn.close()

# ----------------- PREFERENCES -----------------

def set_preference(key, value):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)
    """, (key, value))
    conn.commit()
    conn.close()

def get_preference(key, default=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM preferences WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default

# ----------------- WISHLIST -----------------

def add_wishlist_item(category, colors, pattern=None, sleeve_type=None, season_suitability=None, fabric=None, price=0.0, estimated_wear_count=10, image_path=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO wishlist (category, colors, pattern, sleeve_type, season_suitability, fabric, price, estimated_wear_count, is_purchased, image_path)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
    """, (category, colors, pattern, sleeve_type, season_suitability, fabric, price, estimated_wear_count, image_path))
    conn.commit()
    wish_id = cursor.lastrowid
    conn.close()
    return wish_id

def get_wishlist_items():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM wishlist WHERE is_purchased = 0 ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def mark_wishlist_item_purchased(wish_id, brand=None, purchase_date=None, notes=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Retrieve item
    cursor.execute("SELECT * FROM wishlist WHERE id = ?", (wish_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
        
    item = dict(row)
    
    # Mark as purchased
    cursor.execute("UPDATE wishlist SET is_purchased = 1 WHERE id = ?", (wish_id,))
    
    # Insert into wardrobe
    if not purchase_date:
        purchase_date = datetime.now().strftime("%Y-%m-%d")
        
    wardrobe_id = add_clothing_item(
        category=item['category'],
        colors=item['colors'],
        pattern=item['pattern'],
        sleeve_type=item['sleeve_type'],
        season_suitability=item['season_suitability'],
        fabric=item['fabric'],
        brand=brand,
        purchase_date=purchase_date,
        price=item['price'],
        tags="wishlist_buy",
        notes=notes,
        image_path=item['image_path']
    )
    
    conn.commit()
    conn.close()
    return wardrobe_id

def delete_wishlist_item(wish_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM wishlist WHERE id = ?", (wish_id,))
    conn.commit()
    conn.close()
