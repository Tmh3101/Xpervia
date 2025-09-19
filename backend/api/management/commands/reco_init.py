from django.core.management.base import BaseCommand
from api.services.reco_service.startup import ensure_tfidf_artifacts, ensure_cf_artifacts

class Command(BaseCommand):
    help = "Ensure TF-IDF artifacts exist at startup (build if needed)."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Force rebuild")

    def handle(self, *args, **options):
        # TF-IDF
        self.stdout.write(self.style.MIGRATE_HEADING("Ensuring TF-IDF artifacts..."))
        info_cb = ensure_tfidf_artifacts(force=options.get("force", False))
        if info_cb:
            self.stdout.write(self.style.SUCCESS(f"TF-IDF built: {info_cb}"))
        else:
            self.stdout.write(self.style.SUCCESS("TF-IDF artifacts OK."))

        # CF neighbors
        self.stdout.write(self.style.MIGRATE_HEADING("Ensuring CF user-neighbors..."))
        info_cf = ensure_cf_artifacts()
        if info_cf:
            self.stdout.write(self.style.SUCCESS(f"CF built: {info_cf}"))
        else:
            self.stdout.write(self.style.SUCCESS("CF neighbors OK."))
