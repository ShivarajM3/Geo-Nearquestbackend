import os
import random
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_KEY is missing from environment.")
    exit(1)

try:
    print("Initializing Supabase client...")
    supabase = create_client(url, key)
    
    # Generate a random test email
    test_id = random.randint(1000, 9999)
    test_email = f"test_user_{test_id}@example.com"
    test_name = f"Test User {test_id}"
    test_password = "hashedpassword123"

    print(f"\n1. Testing INSERT into 'users' table with email: {test_email}...")
    insert_res = supabase.table("users").insert({
        "name": test_name,
        "email": test_email,
        "password": test_password
    }).execute()
    
    if insert_res.data:
        print("-> INSERT Success!")
        user_id = insert_res.data[0]["user_id"]
        print(f"Created user record: {insert_res.data[0]}")
        
        print(f"\n2. Testing SELECT from 'users' table for user_id {user_id}...")
        select_res = supabase.table("users").select("*").eq("user_id", user_id).execute()
        if select_res.data:
            print("-> SELECT Success!")
            print(f"Retrieved user record: {select_res.data[0]}")
        else:
            print("-> SELECT Failed: No records returned.")
            
        print(f"\n3. Cleaning up: DELETING test user with user_id {user_id}...")
        # Since we might not have a delete policy, let's try to delete it
        try:
            delete_res = supabase.table("users").delete().eq("user_id", user_id).execute()
            print("-> DELETE completed successfully.")
        except Exception as delete_err:
            print(f"-> DELETE failed (may require delete policies if RLS is on and not using service_role): {delete_err}")
    else:
        print("-> INSERT Failed: No data returned from insert operation.")
        
except Exception as e:
    print(f"\nDatabase verification failed: {e}")
    print("\nPlease ensure you have:")
    print("1. Applied the SQL schema in the Supabase SQL Editor.")
    print("2. Configured the RLS policies (included in 'supabase_schema.sql') if using the anon key, OR")
    print("3. Switched to using the 'service_role' key in backend/.env for secure server-side access.")
