# mysite/supabase_client.py
import os
from supabase import create_client, Client

def get_supabase_server() -> Client:
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_SERVICE_ROLE')  # Service Role para escribir seguro
    if not url or not key:
        raise RuntimeError("Faltan SUPABASE_URL o SUPABASE_SERVICE_ROLE en el entorno.")
    return create_client(url, key)
