from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import (
    landing_page,
    openapi,
    conformance,
    stac_search,
    download_asset,
    STACCollectionViewSet,
    STACItemViewSet
)

router = DefaultRouter()
router.register(r'collections', STACCollectionViewSet, basename='collection')
router.register(r'items', STACItemViewSet, basename='stacitems')

urlpatterns = [
    path('admin/', admin.site.urls),

    path('stac/', landing_page, name='landing-page'),
    path('stac/openapi', openapi, name='openapi-schema'),

    path('stac/conformance', conformance, name='conformance'),
    path('stac/search', stac_search, name='stac-search'),

    path('stac/', include(router.urls)),
    path('assets/<str:filename>', download_asset, name='download-asset'),

]
