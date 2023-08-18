from django.contrib.gis.db import models

from wagtail.models import Page
from wagtailmetadata.models import MetadataPageMixin
from wagtail.admin.panels import FieldPanel

class LocationFeature(models.Model):
    feature = models.CharField(max_length=100,blank=True,null=True)

class Location(models.Model):
    source_id = models.CharField(max_length=100)
    geolocation = models.PointField(srid=4326)
    city = models.CharField(max_length=50)
    features = models.ForeignKey(LocationFeature, on_delete=models.SET_NULL, null=True, blank=True)

class FeaturePage(models.Model):
    feature = models.CharField(max_length=100,blank=True,null=True)

class ModelPage(MetadataPageMixin, Page):
    has_top_layer = models.BooleanField(default=False)
    top_layer = models.CharField(max_length=100)
    locations = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    date_time = models.DateTimeField(auto_now_add=True, null=True)
    source_id = models.CharField(max_length=250, null=True)
    geolocation_x = models.CharField(max_length=250)
    geolocation_y = models.CharField(max_length=250)
    city = models.CharField(max_length=250)
    features = models.ForeignKey(FeaturePage, on_delete=models.SET_NULL, null=True, blank=True)
    api_endpoint = models.URLField()
    email = models.EmailField(null=True)

    content_panels = Page.content_panels + [
        FieldPanel('source_id'),
        FieldPanel('geolocation_x'),
        FieldPanel('geolocation_y'),
        FieldPanel('city'),
        FieldPanel('features'),
    ]



