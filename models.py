"""
Models Documenting Schema Structures for Supabase and SQLite.

Since we are utilizing direct Supabase client queries and raw SQL on local SQLite fallback,
no heavy SQLAlchemy ORM models are required. This file serves as the definitive reference
for table fields, data types, and primary/foreign key mappings.
"""

USERS_TABLE_SCHEMA = {
    "name": "users",
    "columns": {
        "user_id": "SERIAL PRIMARY KEY or INTEGER PRIMARY KEY AUTOINCREMENT",
        "name": "VARCHAR(50) NOT NULL",
        "email": "VARCHAR(50) NOT NULL UNIQUE",
        "password": "VARCHAR(200) NOT NULL"  # Hashed via Werkzeug security
    }
}

USER_PREFERENCES_TABLE_SCHEMA = {
    "name": "user_preferences",
    "columns": {
        "pref_id": "SERIAL PRIMARY KEY or INTEGER PRIMARY KEY AUTOINCREMENT",
        "user_id": "INTEGER REFERENCES users(user_id) ON DELETE CASCADE",
        "mood": "VARCHAR(30)",
        "purpose": "VARCHAR(50)"
    }
}

LOCATIONS_TABLE_SCHEMA = {
    "name": "locations",
    "columns": {
        "location_id": "SERIAL PRIMARY KEY or INTEGER PRIMARY KEY AUTOINCREMENT",
        "place_name": "VARCHAR(100) NOT NULL",
        "category": "VARCHAR(50) NOT NULL",
        "latitude": "FLOAT8 NOT NULL",
        "longitude": "FLOAT8 NOT NULL",
        "rating": "FLOAT8"
    }
}

RECOMMENDATIONS_TABLE_SCHEMA = {
    "name": "recommendations",
    "columns": {
        "rec_id": "SERIAL PRIMARY KEY or INTEGER PRIMARY KEY AUTOINCREMENT",
        "user_id": "INTEGER REFERENCES users(user_id) ON DELETE CASCADE",
        "location_id": "INTEGER REFERENCES locations(location_id) ON DELETE CASCADE",
        "mood": "VARCHAR(30) NOT NULL",
        "timestamp": "TIMESTAMPTZ NOT NULL DEFAULT NOW() / DATETIME DEFAULT CURRENT_TIMESTAMP"
    }
}

SEARCH_HISTORY_TABLE_SCHEMA = {
    "name": "search_history",
    "columns": {
        "search_id": "SERIAL PRIMARY KEY or INTEGER PRIMARY KEY AUTOINCREMENT",
        "user_id": "INTEGER REFERENCES users(user_id) ON DELETE CASCADE",
        "query_text": "VARCHAR(100) NOT NULL",
        "searched_at": "TIMESTAMPTZ NOT NULL DEFAULT NOW() / DATETIME DEFAULT CURRENT_TIMESTAMP"
    }
}
