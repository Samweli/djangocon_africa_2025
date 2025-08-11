
import json
import os

from rest_framework import viewsets

from .models import STACCollection, STACItem, STACAsset
from .serializers import STACCollectionSerializer, STACItemSerializer
from stac_api.renderers import GeoJSONRenderer

from rest_framework.renderers import JSONRenderer

from django.contrib.gis.geos import GEOSGeometry

from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404


from django.conf import settings
from django.urls import reverse

from rest_framework.response import Response
from rest_framework.decorators import action, api_view


@api_view(['GET'])
def landing_page(request):
    base_url = request.build_absolute_uri('/stac/')

    file_path = os.path.join(settings.BASE_DIR, 'api', 'static', 'landing_page.json')

    with open(file_path, 'r') as f:
        data = json.load(f)

    for link in data.get("links", []):
        if "href" in link and "{base_url}" in link["href"]:
            link["href"] = link["href"].replace("{base_url}", base_url)

    return Response(data)

@api_view(['GET'])
def openapi(request):
    # Define path to JSON file
    file_path = os.path.join(settings.BASE_DIR, 'api', 'static', 'openapi.json')

    with open(file_path, 'r') as f:
        data = json.load(f)

    return Response(data, content_type='application/vnd.oai.openapi+json;version=3.0')

@api_view(['GET'])
def conformance(request):
    file_path = os.path.join(settings.BASE_DIR, 'api', 'static', 'conformance.json')
    base_url = request.build_absolute_uri('/stac/')

    with open(file_path, 'r') as f:
        data = json.load(f)
    
    base_url = request.build_absolute_uri("/").rstrip("/")
    for link in data.get("links", []):
        if "href" in link and "{base_url}" in link["href"]:
            link["href"] = link["href"].replace("{base_url}", base_url)

    return Response(data)

@api_view(['GET'])
def download_asset(request, filename):
    try:
        matching_assets = STACAsset.objects.filter(asset_file__endswith=filename)
        asset = matching_assets.first()

    except STACAsset.DoesNotExist:
        raise Http404("Asset not found")

    if not asset.asset_file:
        raise Http404("File not found")

    file_path = asset.asset_file.path
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))


@api_view(['GET', 'POST'])
def stac_search(request):
    print("STAC Search Request Received")

    if request.method == 'POST':
        print(request.data)
    else:
        print(request.query_params)

    # bbox = request.data.get("bbox")
    # datetime_range = request.data.get("datetime")
    # intersects = request.data.get("intersects")

    queryset = STACItem.objects.all()

    # if bbox:
    #     minx, miny, maxx, maxy = bbox
    #     bbox_geom = GEOSGeometry(f'POLYGON(({minx} {miny}, {minx} {maxy}, {maxx} {maxy}, {maxx} {miny}, {minx} {miny}))', srid=4326)
    #     queryset = queryset.filter(geometry__intersects=bbox_geom)

    # if intersects:
    #     geom = GEOSGeometry(str(intersects))
    #     queryset = queryset.filter(geometry__intersects=geom)

    # if datetime_range:
    #     try:
    #         if "/" in datetime_range:
    #             start, end = datetime_range.split("/")
    #             if start:
    #                 queryset = queryset.filter(datetime__gte=start)
    #             if end:
    #                 queryset = queryset.filter(datetime__lte=end)
    #         else:
    #             queryset = queryset.filter(datetime=datetime_range)
    #     except Exception:
    #         console.log("Invalid datetime format in search request")
    #         return Response({"error": "Invalid datetime format"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = STACItemSerializer(queryset, many=True, context={'request': request})
    obj = Response({
        "type": "FeatureCollection",
        "features": serializer.data,
        "context": {
            "matched": 4,
            "returned": 4,
            "limit": 10
        },
        "links": [
            {
            "rel": "self",
            "href": "http://localhost:9000/stac/search"
            }
        ]
    })
    print(obj.data)

    return obj


class STACCollectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = STACCollection.objects.all()
    serializer_class = STACCollectionSerializer
    lookup_field = 'collection_id'
    renderer_classes = [GeoJSONRenderer, JSONRenderer]


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "collections": serializer.data
        })

    
    @action(detail=True, methods=['get'], url_path='items(?:/(?P<item_id>[^/.]+))?')
    def items(self, request, collection_id=None, item_id=None):
        """
        Handles:
         - GET /stac/collections/{collection_id}/items -> list items
         - GET /stac/collections/{collection_id}/items/{item_id} -> get single item
        """

        if item_id:
            item = get_object_or_404(STACItem, item_id=item_id, collection__collection_id=collection_id)
            serializer = STACItemSerializer(item, context={'request': request})
            return Response(serializer.data)

        else:
            items = STACItem.objects.filter(collection__collection_id=collection_id)
            collection = get_object_or_404(STACCollection, collection_id=collection_id)
            serializer = STACItemSerializer(items, many=True, context={'request': request})
            collection_serializer = STACCollectionSerializer(collection, context={'request': request})

            base_url = request.build_absolute_uri('/')[:-1]
            root_url = base_url + reverse('landing-page')
            collection_url = base_url + reverse('collection-detail', kwargs={'collection_id': collection_id})

            links = [
                {
                    "rel": "collection",
                    "type": "application/json",
                    "href": collection_url
                },
                {
                    "rel": "parent",
                    "type": "application/json",
                    "href": collection_url
                },
                {
                    "rel": "root",
                    "type": "application/json",
                    "href": root_url
                },
                {
                    "rel": "self",
                    "type": "application/geo+json",
                    "href": request.build_absolute_uri()
                }
            ]

            return Response({
                "type": "FeatureCollection",
                "features": serializer.data,
                "links": links,
                "stac_version": "1.1.0",
                "id": collection_id,
                "description": collection.description,
                "title": collection.title,
                "license": collection_serializer.data.get('license', 'spdx'),
                "extent": collection_serializer.data.get('extent', {}),
            })


class STACItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = STACItem.objects.all()
    serializer_class = STACItemSerializer
