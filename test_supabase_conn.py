import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

print(f"Supabase URL: {url}")
print(f"Supabase Key: {key[:10]}...{key[-10:] if key else ''}")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_KEY is missing from environment.")
    exit(1)

try:
    print("Initializing Supabase client...")
    supabase = create_client(url, key)
    print("Client initialized. Testing connection by listing/querying users table...")
    
    # Try to query the users table
    try:
        response = supabase.table("users").select("*").limit(1).execute()
        print("Success! Connected to Supabase.")
        print(f"Query response: {response.data}")
    except Exception as query_err:
        print(f"Could not query 'users' table: {query_err}")
        print("This might be because the table does not exist yet. Let's try executing a basic query or checking other tables.")
        
except Exception as e:
    print(f"Failed to connect or initialize: {e}")
