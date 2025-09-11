from django.core.management.base import BaseCommand
from api.services.reco_service.startup import ensure_tfidf_artifacts

class Command(BaseCommand):
    help = "Ensure TF-IDF artifacts exist at startup (build if needed)."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Force rebuild")

    def handle(self, *args, **options):
        info = ensure_tfidf_artifacts(force=options.get("force", False))
        if info:
            self.stdout.write(self.style.SUCCESS(f"TF-IDF built: {info}"))
        else:
            self.stdout.write(self.style.SUCCESS("TF-IDF artifacts OK."))
