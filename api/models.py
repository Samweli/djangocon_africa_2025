from django.contrib.gis.db import models


class STACCollection(models.Model):
    collection_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    extent = models.JSONField()  # Holds bbox and temporal extent

    def __str__(self):
        return self.title


class STACItem(models.Model):
    item_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    geometry = models.GeometryField()
    bbox = models.JSONField()
    datetime = models.DateTimeField()
    collection = models.ForeignKey(STACCollection, related_name='items', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title


class STACAsset(models.Model):
    item = models.ForeignKey(STACItem, related_name='assets', on_delete=models.CASCADE)
    href = models.URLField()
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=100)  # MIME type like "image/tiff; application=geotiff"
    roles = models.JSONField(blank=True, null=True)  # e.g., ["data"], ["thumbnail"]
    asset_file = models.FileField(upload_to='assets/')
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.href}"
