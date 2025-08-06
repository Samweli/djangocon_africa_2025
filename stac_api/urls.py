from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import (
    landing_page,
    conformance,
    stac_search,
    STACCollectionViewSet,
    STACItemViewSet
)

router = DefaultRouter()
router.register(r'collections', STACCollectionViewSet, basename='collection')
router.register(r'items', STACItemViewSet, basename='stacitem')

urlpatterns = [
    path('admin/', admin.site.urls),

    # STAC API root and special endpoints
    path('stac/api/', landing_page, name='landing-page'),
    path('stac/api/conformance', conformance, name='conformance'),
    path('stac/api/search', stac_search, name='stac-search'),

    # Collection and item endpoints
    path('stac/api/', include(router.urls)),
]
