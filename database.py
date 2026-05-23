import os
import sqlite3
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Check if Supabase is configured
is_supabase_configured = (
    SUPABASE_URL 
    and SUPABASE_KEY 
    and "your-project-ref" not in SUPABASE_URL 
    and "your-service-role" not in SUPABASE_KEY
)

supabase: Client = None

if is_supabase_configured:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Connected successfully to Supabase PostgreSQL.")
    except Exception as e:
        print(f"Failed to connect to Supabase: {e}. Falling back to local SQLite database.")
        is_supabase_configured = False
else:
    print("Supabase credentials not configured in backend/.env. Using local SQLite database (geo_nearquest.db).")

# ─── SQLite Fallback Engine Initialization ─────────────────────────────────────
SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), "geo_nearquest.db")

def init_sqlite_db():
    """Initializes the local SQLite database with the required schema."""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    );
    """)
    
    # Create user_preferences table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_preferences (
        pref_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        mood TEXT,
        purpose TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """)
    
    # Create locations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS locations (
        location_id INTEGER PRIMARY KEY AUTOINCREMENT,
        place_name TEXT NOT NULL,
        category TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        rating REAL
    );
    """)
    
    # Create recommendations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recommendations (
        rec_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        location_id INTEGER NOT NULL,
        mood TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE CASCADE
    );
    """)
    
    # Create search_history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS search_history (
        search_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        query_text TEXT NOT NULL,
        searched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """)
    
    conn.commit()
    conn.close()

if not is_supabase_configured:
    init_sqlite_db()

# ─── Abstracted Database Operations ───────────────────────────────────────────

def db_register_user(name, email, password_hash):
    """Registers a new user and returns user data or None if already exists."""
    if is_supabase_configured:
        try:
            # Check if email exists
            res = supabase.table("users").select("*").eq("email", email).execute()
            if res.data:
                return None  # Email taken
            
            insert_res = supabase.table("users").insert({
                "name": name,
                "email": email,
                "password": password_hash
            }).execute()
            
            return insert_res.data[0] if insert_res.data else None
        except Exception as e:
            print(f"Supabase registration error: {e}")
            return None
    else:
        try:
            conn = sqlite3.connect(SQLITE_DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password_hash)
            )
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return {"user_id": user_id, "name": name, "email": email}
        except sqlite3.IntegrityError:
            return None  # Email taken
        except Exception as e:
            print(f"SQLite registration error: {e}")
            return None

def db_get_user_by_email(email):
    """Retrieves a user profile by email."""
    if is_supabase_configured:
        try:
            res = supabase.table("users").select("*").eq("email", email).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            print(f"Supabase get user by email error: {e}")
            return None
    else:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

def db_get_user_by_id(user_id):
    """Retrieves a user profile by user_id."""
    if is_supabase_configured:
        try:
            res = supabase.table("users").select("*").eq("user_id", user_id).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            print(f"Supabase get user by id error: {e}")
            return None
    else:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

def db_get_preferences(user_id):
    """Retrieves saved mood and purpose preferences for a user."""
    if is_supabase_configured:
        try:
            res = supabase.table("user_preferences").select("*").eq("user_id", user_id).execute()
            return res.data[0] if res.data else {"mood": "", "purpose": ""}
        except Exception as e:
            print(f"Supabase get preferences error: {e}")
            return {"mood": "", "purpose": ""}
    else:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT mood, purpose FROM user_preferences WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {"mood": "", "purpose": ""}

def db_save_preferences(user_id, mood, purpose):
    """Saves or updates preferences for a user."""
    if is_supabase_configured:
        try:
            # Check if preferences exist
            res = supabase.table("user_preferences").select("*").eq("user_id", user_id).execute()
            if res.data:
                update_res = supabase.table("user_preferences").update({
                    "mood": mood,
                    "purpose": purpose
                }).eq("user_id", user_id).execute()
                return update_res.data[0] if update_res.data else None
            else:
                insert_res = supabase.table("user_preferences").insert({
                    "user_id": user_id,
                    "mood": mood,
                    "purpose": purpose
                }).execute()
                return insert_res.data[0] if insert_res.data else None
        except Exception as e:
            print(f"Supabase save preferences error: {e}")
            return None
    else:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT pref_id FROM user_preferences WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            cursor.execute(
                "UPDATE user_preferences SET mood = ?, purpose = ? WHERE user_id = ?",
                (mood, purpose, user_id)
            )
        else:
            cursor.execute(
                "INSERT INTO user_preferences (user_id, mood, purpose) VALUES (?, ?, ?)",
                (user_id, mood, purpose)
            )
        conn.commit()
        conn.close()
        return {"user_id": user_id, "mood": mood, "purpose": purpose}

def db_get_history(user_id):
    """Gets search history log for a user, sorted newest first."""
    if is_supabase_configured:
        try:
            res = supabase.table("search_history").select("*").eq("user_id", user_id).order("searched_at", desc=True).execute()
            return res.data
        except Exception as e:
            print(f"Supabase get history error: {e}")
            return []
    else:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT search_id, query_text, searched_at FROM search_history WHERE user_id = ? ORDER BY searched_at DESC",
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

def db_save_history(user_id, query_text):
    """Saves a search query string to the search history."""
    if is_supabase_configured:
        try:
            res = supabase.table("search_history").insert({
                "user_id": user_id,
                "query_text": query_text
            }).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            print(f"Supabase save history error: {e}")
            return None
    else:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO search_history (user_id, query_text) VALUES (?, ?)",
            (user_id, query_text)
        )
        search_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return {"search_id": search_id, "user_id": user_id, "query_text": query_text}

def db_clear_history(user_id):
    """Clears all search history for a user."""
    if is_supabase_configured:
        try:
            supabase.table("search_history").delete().eq("user_id", user_id).execute()
            return True
        except Exception as e:
            print(f"Supabase clear history error: {e}")
            return False
    else:
        try:
            conn = sqlite3.connect(SQLITE_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM search_history WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"SQLite clear history error: {e}")
            return False

def db_get_recommendations(user_id):
    """Retrieves all saved recommendations for a user with location detail."""
    if is_supabase_configured:
        try:
            # Join recommendations and locations in Supabase
            # Since Supabase JS/Py supports join via select, we do:
            res = supabase.table("recommendations").select("*, locations(*)").eq("user_id", user_id).order("timestamp", desc=True).execute()
            
            # Reformat to match flat response
            flat_recs = []
            for item in res.data:
                loc = item.get("locations", {})
                flat_recs.append({
                    "rec_id": item["rec_id"],
                    "place_name": loc.get("place_name", "Unknown Location"),
                    "category": loc.get("category", "General"),
                    "latitude": loc.get("latitude", 0.0),
                    "longitude": loc.get("longitude", 0.0),
                    "rating": loc.get("rating", 0.0),
                    "mood": item["mood"],
                    "timestamp": item["timestamp"]
                })
            return flat_recs
        except Exception as e:
            print(f"Supabase get recommendations error: {e}")
            return []
    else:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.rec_id, l.place_name, l.category, l.latitude, l.longitude, l.rating, r.mood, r.timestamp 
            FROM recommendations r
            JOIN locations l ON r.location_id = l.location_id
            WHERE r.user_id = ?
            ORDER BY r.timestamp DESC
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

def db_save_recommendation(user_id, place_name, category, latitude, longitude, rating, mood):
    """Saves a recommended location and links it to user's saved recommendations list."""
    if is_supabase_configured:
        try:
            # 1. Insert or check location
            # To simplify, we check if location with exact same lat/lng and name exists
            loc_res = supabase.table("locations").select("*").eq("place_name", place_name).eq("latitude", latitude).eq("longitude", longitude).execute()
            
            if loc_res.data:
                location_id = loc_res.data[0]["location_id"]
            else:
                insert_loc = supabase.table("locations").insert({
                    "place_name": place_name,
                    "category": category,
                    "latitude": latitude,
                    "longitude": longitude,
                    "rating": rating
                }).execute()
                location_id = insert_loc.data[0]["location_id"]
            
            # 2. Save recommendation linking to location
            rec_res = supabase.table("recommendations").insert({
                "user_id": user_id,
                "location_id": location_id,
                "mood": mood
            }).execute()
            
            return rec_res.data[0] if rec_res.data else None
        except Exception as e:
            print(f"Supabase save recommendation error: {e}")
            return None
    else:
        try:
            conn = sqlite3.connect(SQLITE_DB_PATH)
            cursor = conn.cursor()
            
            # Check location
            cursor.execute(
                "SELECT location_id FROM locations WHERE place_name = ? AND latitude = ? AND longitude = ?",
                (place_name, latitude, longitude)
            )
            row = cursor.fetchone()
            if row:
                location_id = row[0]
            else:
                cursor.execute(
                    "INSERT INTO locations (place_name, category, latitude, longitude, rating) VALUES (?, ?, ?, ?, ?)",
                    (place_name, category, latitude, longitude, rating)
                )
                location_id = cursor.lastrowid
            
            # Save recommendation
            cursor.execute(
                "INSERT INTO recommendations (user_id, location_id, mood) VALUES (?, ?, ?)",
                (user_id, location_id, mood)
            )
            rec_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return {"rec_id": rec_id, "user_id": user_id, "location_id": location_id, "mood": mood}
        except Exception as e:
            print(f"SQLite save recommendation error: {e}")
            return None
