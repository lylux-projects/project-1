# app/services/supabase_client.py
from supabase import create_client, Client
from app.core.config import settings

supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_anon_key
)

# For admin operations
supabase_admin: Client = create_client(
    settings.supabase_url,
    settings.supabase_service_role_key
)