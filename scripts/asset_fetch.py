from pystac_client import Client
import planetary_computer
import requests
import geopandas as gpd
from shapely.geometry import shape
import os

STAC_API_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"
COLLECTION = "landsat-8-c2-l2"
BBOX = [-122.4, 47.5, -122.2, 47.7]
DATETIME = "2020-07-01/2020-07-31"
ASSET_KEY = "SR_B4"

OUTPUT_DIR = "downloads"
GEOJSON_OUTPUT = "landsat_items.geojson"

os.makedirs(OUTPUT_DIR, exist_ok=True)

catalog = Client.open(STAC_API_URL, modifier=planetary_computer.sign_inplace)

search = catalog.search(
    collections=[COLLECTION],
    bbox=BBOX,
    datetime=DATETIME,
    limit=10
)
items = list(search.get_items())
print(f"Found {len(items)} items")

features = []

for item in items:
    asset = item.assets.get(ASSET_KEY)
    if not asset:
        print(f"No '{ASSET_KEY}' asset found in item {item.id}")
        continue

    # Download the GeoTIFF
    asset_href = planetary_computer.sign(asset.href)
    filename = os.path.join(OUTPUT_DIR, f"{item.id}_{ASSET_KEY}.tif")
    print(f"Downloading {filename} ...")
    with requests.get(asset_href, stream=True) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    feature = {
        "type": "Feature",
        "geometry": item.geometry,
        "properties": {
            "id": item.id,
            "datetime": item.datetime.isoformat(),
            "bbox": item.bbox,
            "platform": item.properties.get("platform"),
            "cloud_cover": item.properties.get("eo:cloud_cover"),
            "asset_file": filename
        }
    }
    features.append(feature)

geojson = {
    "type": "FeatureCollection",
    "features": features
}
gdf = gpd.GeoDataFrame.from_features(geojson)
gdf.to_file(GEOJSON_OUTPUT, driver="GeoJSON")

print(f"\nGeoJSON metadata saved to: {GEOJSON_OUTPUT}")
