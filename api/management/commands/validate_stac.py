from django.core.management.base import BaseCommand
from stac_validator import stac_validator
import requests


STAC_ENDPOINTS = [
    "/stac/",
    "/stac/conformance",
    "/stac/collections/{collection_id}/items",
    "/stac/search",  # optional
]


class Command(BaseCommand):
    help = "Validate your STAC API using the official stac-validator"

    def add_arguments(self, parser):
        parser.add_argument(
            '--base-url',
            type=str,
            default="http://localhost:9000",
            help="Base URL for the STAC API (e.g., https://example.com)"
        )

    def handle(self, *args, **options):
        base_url = options['base_url'].rstrip("/")
        self.stdout.write(f"🔍 Validating STAC API at: {base_url}")

        # Validate landing page
        self._validate_url(f"{base_url}/stac/")

        # Validate static endpoints
        for endpoint in STAC_ENDPOINTS[1:-2]:
            self._validate_url(f"{base_url}{endpoint}")

        # Validate POST /search endpoint (minimal body)
        search_url = f"{base_url}/stac/search"
        self._validate_search(search_url)

        # Get collection IDs dynamically
        collections_url = f"{base_url}/stac/collections"
        collections_resp = requests.get(collections_url)

        self.stdout.write(f"📦 Fetching collections response: {collections_resp}")

        if collections_resp.status_code != 200:
            self.stderr.write("❌ Failed to retrieve collections.")
            return

        collections = collections_resp.json().get("collections", [])
        self.stdout.write(f"📦 Found {len(collections)} collections.")
        for col in collections:

            col_id = col.get("id")
            self.stdout.write(f"📦 Validating collection: {col_id}")
            if not col_id:
                continue

            col_url = f"{base_url}/stac/collections/{col_id}"
            items_url = f"{base_url}/stac/collections/{col_id}/items"

            self.stdout.write(f"📦 Collection URL: {col_url}")
            self.stdout.write(f"📦 Items URL: {items_url}")

            self._validate_url(col_url)
            self._validate_url(items_url)

    def _validate_url(self, url):
        self.stdout.write(f"\n🌐 Validating: {url}")

        try:
            result = stac_validator.StacValidate(url)
            result.run()
            self.stdout.write(f"🔗 Results validation for: {result.message}")

            if result.message[0]["valid_stac"]:
                self.stdout.write(self.style.SUCCESS(f"✅ Valid STAC: {url}"))
            else:
                self.stderr.write(self.style.ERROR(f"❌ Invalid STAC: {url}"))
                for err in result.message.get("errors", []):
                    self.stderr.write(f"  - {err}")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"⚠️  Error validating {url}: {e}"))


    def _validate_search(self, url):
        self.stdout.write(f"\n🌐 Validating POST search endpoint: {url}")

        # Minimal valid POST /search body: empty filters
        body = {"limit": 1}

        try:
            resp = requests.post(url, json=body)
            if resp.status_code != 200:
                self.stderr.write(self.style.ERROR(f"❌ Search POST failed with status {resp.status_code}: {resp.text}"))
                return

            # You can parse and check the response is a FeatureCollection
            data = resp.json()
            if data.get("type") != "FeatureCollection":
                self.stderr.write(self.style.ERROR(f"❌ Search response is not a FeatureCollection: {data.get('type')}"))

            result = stac_validator.StacValidate(url)
            result.run()
            self.stdout.write(f"🔗 Results validation for: {result.message}")

            if result.message[0]["valid_stac"]:
                self.stdout.write(self.style.SUCCESS(f"✅ Valid STAC: {url}"))
            else:
                self.stderr.write(self.style.ERROR(f"❌ Invalid STAC Search endpoint: {url}"))
                for err in result.message.get("errors", []):
                    self.stderr.write(f"  - {err}")

            # Optionally, run stac_validator on the response if your validator supports validation of raw JSON
            # Or save response to a temporary file and validate that file.

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"⚠️ Error during search POST validation at {url}: {e}"))
