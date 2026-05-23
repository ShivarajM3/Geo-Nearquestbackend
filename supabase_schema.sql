-- =============================================================================
-- Geo-Nearquest Supabase Database Schema Setup
-- Run this script in the SQL Editor of your Supabase Dashboard to set up the DB.
-- Project: https://eonrjsnqehjlodpnpmmf.supabase.co
-- =============================================================================

-- ─── 1. Clean Up Existing Tables (Optional, safe re-run) ──────────────────────
-- DROP TABLE IF EXISTS public.search_history;
-- DROP TABLE IF EXISTS public.recommendations;
-- DROP TABLE IF EXISTS public.user_preferences;
-- DROP TABLE IF EXISTS public.locations;
-- DROP TABLE IF EXISTS public.users;

-- ─── 2. Create Users Table ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.users (
    user_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ─── 3. Create User Preferences Table ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.user_preferences (
    pref_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    mood TEXT,
    purpose TEXT,
    CONSTRAINT fk_user_preferences_user FOREIGN KEY (user_id) 
        REFERENCES public.users(user_id) ON DELETE CASCADE
);

-- ─── 4. Create Locations Table ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.locations (
    location_id SERIAL PRIMARY KEY,
    place_name TEXT NOT NULL,
    category TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    rating DOUBLE PRECISION,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_place_coordinates UNIQUE (place_name, latitude, longitude)
);

-- ─── 5. Create Recommendations Table ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.recommendations (
    rec_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    mood TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_recommendations_user FOREIGN KEY (user_id) 
        REFERENCES public.users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_recommendations_location FOREIGN KEY (location_id) 
        REFERENCES public.locations(location_id) ON DELETE CASCADE
);

-- ─── 6. Create Search History Table ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.search_history (
    search_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    query_text TEXT NOT NULL,
    searched_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_search_history_user FOREIGN KEY (user_id) 
        REFERENCES public.users(user_id) ON DELETE CASCADE
);

-- ─── 7. Row Level Security (RLS) Configuration ────────────────────────────────
-- Enable RLS on all tables to secure them.
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.locations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.search_history ENABLE ROW LEVEL SECURITY;

-- ─── 8. RLS Policies ──────────────────────────────────────────────────────────
-- Note: It is HIGHLY RECOMMENDED to configure the Flask backend with your project's
-- 'service_role' key in backend/.env. The 'service_role' key bypasses RLS policies
-- completely, allowing the backend to securely manage read/write actions.
--
-- However, if you are using the 'anon' key for development, the following public policies 
-- must be created to allow access. Uncomment or run these if you are using the 'anon' key.

-- Users Policies
CREATE POLICY "Allow public select for anon key" ON public.users 
    FOR SELECT TO anon USING (true);
CREATE POLICY "Allow public insert for anon key" ON public.users 
    FOR INSERT TO anon WITH CHECK (true);

-- User Preferences Policies
CREATE POLICY "Allow public select for anon key" ON public.user_preferences 
    FOR SELECT TO anon USING (true);
CREATE POLICY "Allow public insert/update for anon key" ON public.user_preferences 
    FOR ALL TO anon USING (true) WITH CHECK (true);

-- Locations Policies
CREATE POLICY "Allow public select for anon key" ON public.locations 
    FOR SELECT TO anon USING (true);
CREATE POLICY "Allow public insert for anon key" ON public.locations 
    FOR INSERT TO anon WITH CHECK (true);

-- Recommendations Policies
CREATE POLICY "Allow public select for anon key" ON public.recommendations 
    FOR SELECT TO anon USING (true);
CREATE POLICY "Allow public insert for anon key" ON public.recommendations 
    FOR INSERT TO anon WITH CHECK (true);

-- Search History Policies
CREATE POLICY "Allow public select/insert/delete for anon key" ON public.search_history 
    FOR ALL TO anon USING (true) WITH CHECK (true);
