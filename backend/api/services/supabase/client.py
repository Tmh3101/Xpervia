from supabase import create_client
from django.conf import settings

supabase_project_url = settings.SUPABASE_PROJECT_URL
supabase_service_role_key = settings.SUPABASE_SERVICE_ROLE_KEY

if not supabase_project_url:
    raise ValueError("SUPABASE_PROJECT_URL is not set in environment variables.")

if not supabase_service_role_key:
    raise ValueError("SUPABASE_SERVICE_ROLE_KEY is not set in environment variables.")

# Tạo client Supabase
supabase = create_client(supabase_project_url, supabase_service_role_key)