from decouple import config
import json
import logging
import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from django.apps import apps as django_apps
from django.db.utils import IntegrityError

logger = logging.getLogger(__name__)


def _get_env(name: str, default: str | None = None) -> str | None:
    return config(name, default=default)

def _supabase_headers(service_role_key: str) -> dict:
    return {
        "apikey": service_role_key,
        "Authorization": f"Bearer {service_role_key}",
        "Content-Type": "application/json",
    }


def _find_supabase_user_by_email(supabase_url: str, headers: dict, email: str):
    """
    GET /auth/v1/admin/users?email=...
    Returns a single user dict if exists, else None.
    """
    url = f"{supabase_url.rstrip('/')}/auth/v1/admin/users"
    try:
        resp = requests.get(url, headers=headers, params={"email": email}, timeout=10)
        if resp.status_code == 200:
            payload = resp.json()
            # payload may contain {"users": [...]} or similar depending supabase responses
            users = payload.get("users") if isinstance(payload, dict) else None
            if users:
                return users[0]
            # some supabase deployments return a list directly
            if isinstance(payload, list) and payload:
                return payload[0]
        else:
            logger.warning("Supabase lookup returned %s: %s", resp.status_code, resp.text)
    except Exception as e:
        logger.exception("Exception while looking up supabase user: %s", e)
    return None


def _create_supabase_user(supabase_url: str, headers: dict, email: str, password: str, first_name: str, last_name: str, role: str):
    """
    POST /auth/v1/admin/users
    - uses app_metadata for role (writeable only by service role).
    - returns created user dict or None.
    """
    url = f"{supabase_url.rstrip('/')}/auth/v1/admin/users"
    body = {
        "email": email,
        "password": password,
        "user_metadata": {
            "first_name": first_name,
            "last_name": last_name,
            "role": role
        },
        # confirm email immediately so account usable; optional
        "email_confirm": True
    }
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=10)
        if resp.status_code in (200, 201):
            # Response content might be {'id':..., ...} or {'user': {...}} depending on versions
            return resp.json()
        else:
            logger.warning("Supabase create user failed %s: %s", resp.status_code, resp.text)
    except Exception as e:
        logger.exception("Exception while creating supabase user: %s", e)
    return None


class Command(BaseCommand):
    help = "Seed admin user into Supabase Auth and create local shadow user record."

    def add_arguments(self, parser):
        parser.add_argument(
            "--email", dest="email", help="Admin email (overrides ADMIN_EMAIL env)", default=None
        )
        parser.add_argument(
            "--password", dest="password", help="Admin password (overrides ADMIN_PASSWORD env)", default=None
        )

    def handle(self, *args, **options):
        # Load config from env or CLI
        supabase_url = _get_env("SUPABASE_PROJECT_URL")
        service_role_key = _get_env("SUPABASE_SERVICE_ROLE_KEY")

        if not supabase_url:
            self.stderr.write(self.style.ERROR("SUPABASE_PROJECT_URL is not set. Abort."))
            return
        if not service_role_key:
            self.stderr.write(self.style.ERROR("SUPABASE_SERVICE_ROLE_KEY is not set. Abort."))
            return

        admin_email = options["email"] or _get_env("ADMIN_EMAIL", "admin001@gmail.com")
        admin_password = options["password"] or _get_env("ADMIN_PASSWORD", "admin001")
        admin_first_name = _get_env("ADMIN_FIRST_NAME", "Admin")
        admin_last_name = _get_env("ADMIN_LAST_NAME", "User")
        admin_role = _get_env("ADMIN_ROLE", "admin")

        headers = _supabase_headers(service_role_key)

        # get User model dynamically to avoid import time issues
        try:
            User = django_apps.get_model("api", "User")
        except LookupError as e:
            self.stderr.write(self.style.ERROR(f"Cannot find User model 'api.User': {e}"))
            return

        # 0) Check local DB first: by role OR by email
        try:
            exists_by_role = User.objects.filter(role=admin_role).exists()
            exists_by_email = User.objects.filter(email=admin_email).exists()
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"DB query failed: {e}"))
            logger.exception("DB query failed during seed admin.")
            return

        if exists_by_role or exists_by_email:
            self.stdout.write(self.style.WARNING("Admin already exists in local DB. Skipping creation."))
            return

        # 1) Check Supabase for existing user by email
        supabase_user = _find_supabase_user_by_email(supabase_url, headers, admin_email)

        # 2) If not found in Supabase -> create
        if not supabase_user:
            self.stdout.write("Creating admin user in Supabase...")
            created = _create_supabase_user(
                supabase_url=supabase_url,
                headers=headers,
                email=admin_email,
                password=admin_password,
                first_name=admin_first_name,
                last_name=admin_last_name,
                role=admin_role,
            )
            if not created:
                self.stderr.write(self.style.ERROR("Failed to create user in Supabase. Check logs."))
                return
            # normalize response
            if isinstance(created, dict) and "user" in created:
                supabase_user = created["user"]
            else:
                supabase_user = created

        # 3) Extract supabase user id and email
        supabase_user_id = supabase_user.get("id") or supabase_user.get("user", {}).get("id")
        supabase_user_email = supabase_user.get("email") or supabase_user.get("user", {}).get("email", admin_email)

        if not supabase_user_id:
            self.stderr.write(self.style.ERROR("Supabase user payload is missing 'id'. Cannot create local user."))
            logger.error("Supabase payload: %s", json.dumps(supabase_user))
            return

        # 4) Create shadow user in local DB with id = supabase_user_id
        try:
            with transaction.atomic():
                User.objects.create(
                    id=supabase_user_id,
                    email=supabase_user_email,
                    first_name=admin_first_name,
                    last_name=admin_last_name,
                    role=admin_role,
                )
        except IntegrityError as e:
            self.stderr.write(self.style.ERROR(f"IntegrityError creating local user: {e}"))
            logger.exception("IntegrityError creating local user.")
            return
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to create local user: {e}"))
            logger.exception("Failed to create local user.")
            return

        self.stdout.write(self.style.SUCCESS(f"Admin created: {admin_email} (id={supabase_user_id})"))
        logger.info("Admin created: %s (id=%s)", admin_email, supabase_user_id)
