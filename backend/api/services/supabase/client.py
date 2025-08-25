from supabase import create_client
from django.conf import settings

# Tạo client Supabase
supabase = create_client(settings.SUPABASE_PROJECT_URL, settings.SUPABASE_SERVICE_ROLE_KEY)