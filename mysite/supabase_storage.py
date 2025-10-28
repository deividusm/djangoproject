from supabase import create_client, Client
from django.conf import settings

def get_supabase_client() -> Client:
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_API_KEY
    return create_client(url, key)

# ejemplo
