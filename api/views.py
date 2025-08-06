
import json
import os

from rest_framework import viewsets
from .models import STACCollection, STACItem
from .serializers import STACCollectionSerializer, STACItemSerializer

from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def landing_page(request):
    base_url = request.build_absolute_uri('/stac/api/')

    # Define path to JSON file
    file_path = os.path.join(settings.BASE_DIR, 'api', 'static', 'landing_page.json')

    with open(file_path, 'r') as f:
        data = json.load(f)

    # Replace placeholders
    for link in data.get("links", []):
        if "href" in link and "{base_url}" in link["href"]:
            link["href"] = link["href"].replace("{base_url}", base_url)

    return Response(data)

@api_view(['GET'])
def conformance(request):
    file_path = os.path.join(settings.BASE_DIR, 'api', 'static', 'conformance.json')

    with open(file_path, 'r') as f:
        data = json.load(f)

    return Response(data)


@api_view(['POST'])
def stac_search(request):
    bbox = request.data.get("bbox")
    datetime_range = request.data.get("datetime")
    intersects = request.data.get("intersects")

    queryset = STACItem.objects.all()

    if bbox:
        minx, miny, maxx, maxy = bbox
        bbox_geom = GEOSGeometry(f'POLYGON(({minx} {miny}, {minx} {maxy}, {maxx} {maxy}, {maxx} {miny}, {minx} {miny}))', srid=4326)
        queryset = queryset.filter(geometry__intersects=bbox_geom)

    if intersects:
        geom = GEOSGeometry(str(intersects))
        queryset = queryset.filter(geometry__intersects=geom)

    if datetime_range:
        try:
            if "/" in datetime_range:
                start, end = datetime_range.split("/")
                if start:
                    queryset = queryset.filter(datetime__gte=start)
                if end:
                    queryset = queryset.filter(datetime__lte=end)
            else:
                queryset = queryset.filter(datetime=datetime_range)
        except Exception:
            return Response({"error": "Invalid datetime format"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = STACItemSerializer(queryset, many=True, context={'request': request})
    return Response({
        "type": "FeatureCollection",
        "features": serializer.data
    })


class STACCollectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = STACCollection.objects.all()
    serializer_class = STACCollectionSerializer


class STACItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = STACItem.objects.all()
    serializer_class = STACItemSerializer
