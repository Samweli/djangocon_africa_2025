from rest_framework import serializers
from .models import STACCollection, STACItem, STACAsset


class STACAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = STACAsset
        fields = [
            'href', 'title', 'type', 'roles', 'asset_file', 'thumbnail'
        ]


class STACItemSerializer(serializers.ModelSerializer):
    assets = STACAssetSerializer(many=True, read_only=True)
    geometry = serializers.SerializerMethodField()
    bbox = serializers.SerializerMethodField()
    properties = serializers.SerializerMethodField()
    collection = serializers.SlugRelatedField(slug_field='collection_id', queryset=STACCollection.objects.all())

    class Meta:
        model = STACItem
        fields = [
            'item_id', 'title', 'description', 'geometry', 'bbox',
            'datetime', 'properties', 'collection', 'assets'
        ]

    def get_geometry(self, obj):
        return obj.geometry.geojson if obj.geometry else None

    def get_bbox(self, obj):
        return obj.bbox

    def get_properties(self, obj):
        return {
            "datetime": obj.datetime.isoformat()
        }


class STACCollectionSerializer(serializers.ModelSerializer):
    items = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = STACCollection
        fields = [
            'collection_id', 'title', 'description', 'extent', 'items'
        ]
