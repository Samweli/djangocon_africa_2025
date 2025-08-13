import json
import os
from django.contrib.gis.geos import GEOSGeometry
from django.utils.dateparse import parse_datetime

from api.models import STACItem, STACAsset, STACCollection

# Path to your file
json_file_path = './scripts/landsat_items.geojson'

# Set collection_id (must exist or will be created)
collection_id = 'landsat-8'
collection, _ = STACCollection.objects.get_or_create(
    collection_id=collection_id,
    defaults={
        "title": "Landsat-8 Collection",
        "description": "Imported Landsat-8 Items",
        "extent": {}  # You can enhance with bbox + datetime range if needed
    }
)

# Load JSON
with open(json_file_path, 'r') as f:
    data = json.load(f)

features = data.get("features", [])

for feature in features:
    props = feature["properties"]
    geom = feature["geometry"]
    
    item_id = props["id"]
    datetime_str = props["datetime"]
    bbox = props["bbox"]
    asset_file = props["asset_file"]

    # Create STAC Item
    item, created = STACItem.objects.get_or_create(
        item_id=item_id,
        defaults={
            "title": item_id,
            "description": f"Landsat item from {datetime_str}",
            "geometry": GEOSGeometry(json.dumps(geom)),
            "bbox": bbox,
            "datetime": parse_datetime(datetime_str),
            "collection": collection,
        }
    )

    if created:
        print(f"Imported item: {item_id}")
    else:
        print(f"Skipped existing item: {item_id}")
        continue

    # Create associated Asset
    STACAsset.objects.create(
        item=item,
        href=asset_file,
        title=f"{item_id} Asset",
        type="image/tiff; application=geotiff",
        roles=["data"],
        asset_file=asset_file
    )

    print(f"  → Asset added for {item_id}")
