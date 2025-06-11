# app/services/supabase_client.py
from supabase import create_client, Client
from app.core.config import settings

supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_anon_key  # Now matches the .env file
)

# For admin operations - now you can uncomment this since you have the service role key
supabase_admin: Client = create_client(
    settings.supabase_url,
    settings.supabase_service_role_key
)