import json

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import STACCollection, STACItem, STACAsset


class STACAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = STACAsset
        fields = [
            'href', 'title', 'type', 'roles', 'asset_file', 'thumbnail'
        ]


class STACItemSerializer(serializers.ModelSerializer):
    assets = serializers.SerializerMethodField()
    geometry = serializers.SerializerMethodField()
    bbox = serializers.SerializerMethodField()
    properties = serializers.SerializerMethodField()
    collection = serializers.SlugRelatedField(slug_field='collection_id', queryset=STACCollection.objects.all())
    type = serializers.SerializerMethodField()
    id = serializers.CharField(source='item_id')
    links = serializers.SerializerMethodField()

    class Meta:
        model = STACItem
        fields = [
            'type', 'id', 'collection', 'geometry', 'bbox',
            'properties', 'assets', 'links'
        ]

    def get_type(self, obj):
        return "Feature"

    def get_geometry(self, obj):
        if not obj.geometry:
            return None
        if isinstance(obj.geometry.geojson, str):
            return json.loads(obj.geometry.geojson)
        return obj.geometry.geojson

    def get_bbox(self, obj):
        return obj.bbox

    def get_properties(self, obj):
        return {
            "datetime": obj.datetime.isoformat() if obj.datetime else None,
            "title": obj.title,
            "description": obj.description,
        }

    def get_assets(self, obj):
        assets_qs = obj.assets.all()
        assets_dict = {}
        for asset in assets_qs:
            key = asset.title or asset.href
            assets_dict[key] = {
                "href": asset.href,
                "title": asset.title,
                "type": asset.type,
                "roles": asset.roles if asset.roles else [],
            }
        return assets_dict

    def get_links(self, obj):
        base_url = self.context.get('request').build_absolute_uri('/') if self.context.get('request') else ''
        return [
            {
                "rel": "self",
                "href": f"{base_url}stac/collections/{obj.collection.collection_id}/items/{obj.item_id}"
            },
            {
                "rel": "collection",
                "href": f"{base_url}stac/collections/{obj.collection.collection_id}"
            }
        ]


class STACCollectionSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='collection_id') 
    type = serializers.SerializerMethodField()
    links = serializers.SerializerMethodField()
    stac_version = serializers.SerializerMethodField()
    license = serializers.CharField(default="spdx")
    extent = serializers.SerializerMethodField()


    class Meta:
        model = STACCollection
        fields = [
            'id', 'type', 'title', 'description', 'extent', 'links', 'stac_version', 'license', 'extent'
        ]

    def get_extent(self, obj):
        return {
            "spatial": {
                "bbox": [obj.extent] if obj.extent else []
            },
            "temporal": {
                "interval": [
                    ["2020-07-01T00:00:00Z", "2020-08-01T00:00:00Z"]
                ]
            }
        }
    
    def get_stac_version(self, obj):
        return "1.1.0"

    def get_type(self, obj):
        return "Collection"

    def get_links(self, obj):
        request = self.context.get('request')
        base_url = request.build_absolute_uri('/')[:-1] if request else ''
        return [
            {
                "rel": "self",
                "href": f"{base_url}/stac/collections/{obj.collection_id}",
                "type": "application/json"
            },
            {
                "rel": "root",
                "href": f"{base_url}/stac",
                "type": "application/json"
            },
            {
                "rel": "items",
                "href": f"{base_url}/stac/collections/{obj.collection_id}/items",
                "type": "application/geo+json"
            }
        ]
