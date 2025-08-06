from django.core.management.base import BaseCommand
from stac_validator import stac_validator
import requests


STAC_ENDPOINTS = [
    "/stac/api/",
    "/stac/api/conformance",
    "/stac/api/collections",
    "/stac/api/collections/{collection_id}",
    "/stac/api/collections/{collection_id}/items",
    "/stac/api/search",  # optional
]


class Command(BaseCommand):
    help = "Validate your STAC API using the official stac-validator"

    def add_arguments(self, parser):
        parser.add_argument(
            '--base-url',
            type=str,
            default="http://localhost:9000/stac/api/",
            help="Base URL for the STAC API (e.g., https://example.com)"
        )

    def handle(self, *args, **options):
        base_url = options['base_url'].rstrip("/")
        self.stdout.write(f"🔍 Validating STAC API at: {base_url}")

        # Validate landing page
        self._validate_url(f"{base_url}/stac/api/")

        # Validate static endpoints
        for endpoint in STAC_ENDPOINTS[1:-2]:
            self._validate_url(f"{base_url}{endpoint}")

        # Get collection IDs dynamically
        collections_url = f"{base_url}/stac/api/collections"
        collections_resp = requests.get(collections_url)

        if collections_resp.status_code != 200:
            self.stderr.write("❌ Failed to retrieve collections.")
            return

        collections = collections_resp.json().get("collections", [])
        for col in collections:
            col_id = col.get("id")
            if not col_id:
                continue

            col_url = f"{base_url}/stac/api/collections/{col_id}"
            items_url = f"{base_url}/stac/api/collections/{col_id}/items"

            self._validate_url(col_url)
            self._validate_url(items_url)

    def _validate_url(self, url):
        self.stdout.write(f"\n🌐 Validating: {url}")
        try:
            result = stac_validator.StacValidate(url=url)
            result.run()
            if result.message["valid"]:
                self.stdout.write(self.style.SUCCESS(f"✅ Valid STAC: {url}"))
            else:
                self.stderr.write(self.style.ERROR(f"❌ Invalid STAC: {url}"))
                for err in result.message.get("errors", []):
                    self.stderr.write(f"  - {err}")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"⚠️  Error validating {url}: {e}"))
