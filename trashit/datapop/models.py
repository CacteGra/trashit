from django.contrib.gis.db import models


from wagtail.snippets.views.snippets import SnippetViewSet, IndexView, EditView

from wagtail.models import Page, Orderable
from modelcluster.models import ClusterableModel
from wagtailmetadata.models import MetadataPageMixin
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.admin.panels import FieldPanel, MultipleChooserPanel

from wagtail.snippets.models import register_snippet

from .widgets import ChosenChooserWidget, OperatedChooserWidget


class Booleanfield(models.Model):
    id = models.BigAutoField(primary_key=True)
    data_line = models.ForeignKey('DataLine', on_delete=models.CASCADE, null=True, blank=True)
    register_api_chosen = models.ForeignKey('RegisterAPIChosen', on_delete=models.SET_NULL, null=True, blank=True)
    operated_field = models.ForeignKey('OperatedField', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    o_field = models.BooleanField(null=True, blank=True)
    is_up = models.BooleanField(default=False)


    def __str__(self):
        return "%s" % (self._meta.object_name)

class Charfield(models.Model):
    id = models.BigAutoField(primary_key=True)
    data_line = models.ForeignKey('DataLine', on_delete=models.CASCADE, null=True, blank=True)
    register_api_chosen = models.ForeignKey('RegisterAPIChosen', on_delete=models.SET_NULL, null=True, blank=True)
    operated_field = models.ForeignKey('OperatedField', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    o_field = models.CharField(null=True, blank=True)
    is_up = models.BooleanField(default=False)


    def __str__(self):
        return "%s" % (self._meta.object_name)


class Datefield(models.Model):
    id = models.BigAutoField(primary_key=True)
    data_line = models.ForeignKey('DataLine', on_delete=models.CASCADE, null=True, blank=True)
    register_api_chosen = models.ForeignKey('RegisterAPIChosen', on_delete=models.SET_NULL, null=True, blank=True)
    operated_field = models.ForeignKey('OperatedField', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    o_field = models.DateField(null=True, blank=True)
    is_up = models.BooleanField(default=False)


    def __str__(self):
        return "%s" % (self._meta.object_name)


class Datetimefield(models.Model):
    id = models.BigAutoField(primary_key=True)
    data_line = models.ForeignKey('DataLine', on_delete=models.CASCADE, null=True, blank=True)
    register_api_chosen = models.ForeignKey('RegisterAPIChosen', on_delete=models.SET_NULL, null=True, blank=True)
    operated_field = models.ForeignKey('OperatedField', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    o_field = models.DateTimeField(null=True, blank=True)
    is_up = models.BooleanField(default=False)


    def __str__(self):
        return "%s" % (self._meta.object_name)


class Emailfield(models.Model):
    id = models.BigAutoField(primary_key=True)
    data_line = models.ForeignKey('DataLine', on_delete=models.CASCADE, null=True, blank=True)
    register_api_chosen = models.ForeignKey('RegisterAPIChosen', on_delete=models.SET_NULL, null=True, blank=True)
    operated_field = models.ForeignKey('OperatedField', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    o_field = models.EmailField(null=True, blank=True)
    is_up = models.BooleanField(default=False)


    def __str__(self):
        return "%s" % (self._meta.object_name)


class Filepathfield(models.Model):
    id = models.BigAutoField(primary_key=True)
    data_line = models.ForeignKey('DataLine', on_delete=models.CASCADE, null=True, blank=True)
    register_api_chosen = models.ForeignKey('RegisterAPIChosen', on_delete=models.SET_NULL, null=True, blank=True)
    operated_field = models.ForeignKey('OperatedField', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    o_field = models.FilePathField(null=True, blank=True)
    is_up = models.BooleanField(default=False)


    def __str__(self):
        return "%s" % (self._meta.object_name)


class Floatfield(models.Model):
    id = models.BigAutoField(primary_key=True)
    data_line = models.ForeignKey('DataLine', on_delete=models.CASCADE, null=True, blank=True)
    register_api_chosen = models.ForeignKey('RegisterAPIChosen', on_delete=models.SET_NULL, null=True, blank=True)
    operated_field = models.ForeignKey('OperatedField', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    o_field = models.FloatField(null=True, blank=True)
    is_up = models.BooleanField(default=False)


    def __str__(self):
        return "%s" % (self._meta.object_name)


class Integerfield(models.Model):
    id = models.BigAutoField(primary_key=True)
    data_line = models.ForeignKey('DataLine', on_delete=models.CASCADE, null=True, blank=True)
    register_api_chosen = models.ForeignKey('RegisterAPIChosen', on_delete=models.SET_NULL, null=True, blank=True)
    operated_field = models.ForeignKey('OperatedField', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    o_field = models.IntegerField(null=True, blank=True)
    is_up = models.BooleanField(default=False)


    def __str__(self):
        return "%s" % (self._meta.object_name)


class Positiveintegerfield(models.Model):
    id = models.BigAutoField(primary_key=True)
    data_line = models.ForeignKey('DataLine', on_delete=models.CASCADE, null=True, blank=True)
    register_api_chosen = models.ForeignKey('RegisterAPIChosen', on_delete=models.SET_NULL, null=True, blank=True)
    operated_field = models.ForeignKey('OperatedField', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    o_field = models.PositiveIntegerField(null=True, blank=True)
    is_up = models.BooleanField(default=False)


    def __str__(self):
        return "%s" % (self._meta.object_name)


class Textfield(models.Model):
    id = models.BigAutoField(primary_key=True)
    data_line = models.ForeignKey('DataLine', on_delete=models.CASCADE, null=True, blank=True)
    register_api_chosen = models.ForeignKey('RegisterAPIChosen', on_delete=models.SET_NULL, null=True, blank=True)
    operated_field = models.ForeignKey('OperatedField', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    o_field = models.TextField(null=True, blank=True)
    is_up = models.BooleanField(default=False)


    def __str__(self):
        return "%s" % (self._meta.object_name)


class Timefield(models.Model):
    id = models.BigAutoField(primary_key=True)
    data_line = models.ForeignKey('DataLine', on_delete=models.CASCADE, null=True, blank=True)
    register_api_chosen = models.ForeignKey('RegisterAPIChosen', on_delete=models.SET_NULL, null=True, blank=True)
    operated_field = models.ForeignKey('OperatedField', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    o_field = models.TimeField(null=True, blank=True)
    is_up = models.BooleanField(default=False)


    def __str__(self):
        return "%s" % (self._meta.object_name)


class Urlfield(models.Model):
    id = models.BigAutoField(primary_key=True)
    data_line = models.ForeignKey('DataLine', on_delete=models.CASCADE, null=True, blank=True)
    register_api_chosen = models.ForeignKey('RegisterAPIChosen', on_delete=models.SET_NULL, null=True, blank=True)
    operated_field = models.ForeignKey('OperatedField', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    o_field = models.URLField(null=True, blank=True)
    is_up = models.BooleanField(default=False)


    def __str__(self):
        return "%s" % (self._meta.object_name)


class Filefield(models.Model):
    id = models.BigAutoField(primary_key=True)
    data_line = models.ForeignKey('DataLine', on_delete=models.CASCADE, null=True, blank=True)
    register_api_chosen = models.ForeignKey('RegisterAPIChosen', on_delete=models.SET_NULL, null=True, blank=True)
    operated_field = models.ForeignKey('OperatedField', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    o_field = models.FileField(null=True, blank=True)
    is_up = models.BooleanField(default=False)


    def __str__(self):
        return "%s" % (self._meta.object_name)

class Imagefield(models.Model):
    id = models.BigAutoField(primary_key=True)
    data_line = models.ForeignKey('DataLine', on_delete=models.CASCADE, null=True, blank=True)
    register_api_chosen = models.ForeignKey('RegisterAPIChosen', on_delete=models.SET_NULL, null=True, blank=True)
    operated_field = models.ForeignKey('OperatedField', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    o_field = models.ImageField(null=True, blank=True)
    is_up = models.BooleanField(default=False)


    def __str__(self):
        return "%s" % (self._meta.object_name)

class Jsonfield(models.Model):
    id = models.BigAutoField(primary_key=True)
    data_line = models.ForeignKey('DataLine', on_delete=models.CASCADE, null=True, blank=True)
    register_api_chosen = models.ForeignKey('RegisterAPIChosen', on_delete=models.SET_NULL, null=True, blank=True)
    operated_field = models.ForeignKey('OperatedField', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    o_field = models.JSONField(null=True, blank=True)
    is_up = models.BooleanField(default=False)


    def __str__(self):
        return "%s" % (self._meta.object_name)

class Geometrycollectionfield(models.Model):
    id = models.BigAutoField(primary_key=True)
    data_line = models.ForeignKey('DataLine', on_delete=models.CASCADE, null=True, blank=True)
    register_api_chosen = models.ForeignKey('RegisterAPIChosen', on_delete=models.SET_NULL, null=True, blank=True)
    operated_field = models.ForeignKey('OperatedField', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    o_field = models.GeometryCollectionField(null=True, blank=True)
    is_up = models.BooleanField(default=False)


    def __str__(self):
        return "%s" % (self._meta.object_name)

class Geometryfield(models.Model):
    id = models.BigAutoField(primary_key=True)
    data_line = models.ForeignKey('DataLine', on_delete=models.CASCADE, null=True, blank=True)
    register_api_chosen = models.ForeignKey('RegisterAPIChosen', on_delete=models.SET_NULL, null=True, blank=True)
    operated_field = models.ForeignKey('OperatedField', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    o_field = models.GeometryField(null=True, blank=True)
    is_up = models.BooleanField(default=False)


    def __str__(self):
        return "%s" % (self._meta.object_name)

class Linestringfield(models.Model):
    id = models.BigAutoField(primary_key=True)
    data_line = models.ForeignKey('DataLine', on_delete=models.CASCADE, null=True, blank=True)
    register_api_chosen = models.ForeignKey('RegisterAPIChosen', on_delete=models.SET_NULL, null=True, blank=True)
    operated_field = models.ForeignKey('OperatedField', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    o_field = models.LineStringField(null=True, blank=True)
    is_up = models.BooleanField(default=False)


    def __str__(self):
        return "%s" % (self._meta.object_name)

class Multilinestringfield(models.Model):
    id = models.BigAutoField(primary_key=True)
    data_line = models.ForeignKey('DataLine', on_delete=models.CASCADE, null=True, blank=True)
    register_api_chosen = models.ForeignKey('RegisterAPIChosen', on_delete=models.SET_NULL, null=True, blank=True)
    operated_field = models.ForeignKey('OperatedField', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    o_field = models.MultiLineStringField(null=True, blank=True)
    is_up = models.BooleanField(default=False)


    def __str__(self):
        return "%s" % (self._meta.object_name)


class Multipointfield(models.Model):
    id = models.BigAutoField(primary_key=True)
    data_line = models.ForeignKey('DataLine', on_delete=models.CASCADE, null=True, blank=True)
    register_api_chosen = models.ForeignKey('RegisterAPIChosen', on_delete=models.SET_NULL, null=True, blank=True)
    operated_field = models.ForeignKey('OperatedField', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    o_field = models.MultiPointField(null=True, blank=True)
    is_up = models.BooleanField(default=False)


    def __str__(self):
        return "%s" % (self._meta.object_name)

class Multipolygonfield(models.Model):
    id = models.BigAutoField(primary_key=True)
    data_line = models.ForeignKey('DataLine', on_delete=models.CASCADE, null=True, blank=True)
    register_api_chosen = models.ForeignKey('RegisterAPIChosen', on_delete=models.SET_NULL, null=True, blank=True)
    operated_field = models.ForeignKey('OperatedField', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    o_field = models.MultiPolygonField(null=True, blank=True)
    is_up = models.BooleanField(default=False)


    def __str__(self):
        return "%s" % (self._meta.object_name)

class Pointfield(models.Model):
    id = models.BigAutoField(primary_key=True)
    data_line = models.ForeignKey('DataLine', on_delete=models.CASCADE, null=True, blank=True)
    register_api_chosen = models.ForeignKey('RegisterAPIChosen', on_delete=models.SET_NULL, null=True, blank=True)
    operated_field = models.ForeignKey('OperatedField', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    o_field = models.PointField(null=True, blank=True)
    is_up = models.BooleanField(default=False)


    def __str__(self):
        return "%s" % (self._meta.object_name)

class Polygonfield(models.Model):
    id = models.BigAutoField(primary_key=True)
    data_line = models.ForeignKey('DataLine', on_delete=models.CASCADE, null=True, blank=True)
    register_api_chosen = models.ForeignKey('RegisterAPIChosen', on_delete=models.SET_NULL, null=True, blank=True)
    operated_field = models.ForeignKey('OperatedField', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    o_field = models.PolygonField(srid=4326, null=True, blank=True)
    is_up = models.BooleanField(default=False)


    def __str__(self):
        return "%s" % (self._meta.object_name)


class LocationFeature(models.Model):
    feature = models.CharField(max_length=100,blank=True,null=True)

class Location(models.Model):
    source_id = models.CharField(max_length=100)
    geolocation = models.PointField(srid=4326)
    city = models.CharField(max_length=50)
    features = models.ForeignKey(LocationFeature, on_delete=models.SET_NULL, null=True)

class DataLine(models.Model):
    register_api = models.ForeignKey('RegisterAPI', on_delete=models.CASCADE, null=True, blank=True)
    register_api_chosen = models.ManyToManyField('RegisterAPIChosen', blank=True)
    line_id = models.PositiveIntegerField(null=True, blank=True)
    line_number = models.PositiveIntegerField(null=True, blank=True)
    the_time = models.DateTimeField(auto_now_add=True)

class Chosen(models.Model):
    text_chosen = models.CharField(null=True, blank=True)
    value_example = models.CharField(null=True, blank=True)
    def __str__(self):
        return "%s" % (self.text_chosen)

class RegisterAPIChosen(Orderable, models.Model):
    register_api = ParentalKey("RegisterAPI", related_name="the_api", on_delete=models.CASCADE, null=True, blank=True)
    register_api_foreign = models.ForeignKey('RegisterAPI', on_delete=models.CASCADE, null=True, blank=True)
    # operated_select = ParentalManyToManyField("OperatedField", related_name="the_operated", blank=True)
    # operated_select_foreign = models.ForeignKey('OperatedField', on_delete=models.CASCADE, null=True, blank=True)
    hierarchy = models.PositiveIntegerField(null=True, blank=True)
    children_of = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    line_id = models.ForeignKey('self', related_name='the_id', on_delete=models.SET_NULL, null=True, blank=True)
    chosen = models.ForeignKey(
        "Chosen", related_name="chosen", on_delete=models.CASCADE, null=True, blank=True
    )
    ticked = models.BooleanField(default=False)
    is_list = models.BooleanField(default=False)

    FIELD_CHOICES = [
        ("Booleanfield", "BooleanField"),
        ("Charfield", "CharField"),
        ("Datefield", "DateField"),
        ("Datetimefield", "DateTimeField"),
        ("Emailfield", "EmailField"),
        ("Filepathfield", "FilePathField"),
        ("Floatfield", "FloatField"),
        ("Integerfield", "IntegerField"),
        ("Positiveintegerfield", "PositiveIntegerField"),
        ("Textfield", "TextField"),
        ("Timefield", "TimeField"),
        ("Urlfield", "URLField"),
        ("Filefield", "FileField"),
        ("Imagefield", "ImageField"),
        ("Jsonfield", "JSONField"),
        ("Geometrycollectionfield", "GeometryCollectionField"),
        ("Geometryfield", "GeometryField"),
        ("Linestringfield", "LinestringField"),
        ("Multilinestringfield", "MultiLineStringField"),
        ("Multipointfield", "MultiPointField"),
        ("Multipolygonfield", "MultiPolygonField"),
        ("Pointfield", "PointField"),
        ("Polygonfield", "PolygonField"),
    ]

    field_type = models.CharField(
        max_length=23,
        choices=FIELD_CHOICES,
        null=True, blank=True
    )

    panels = [FieldPanel("chosen", widget=ChosenChooserWidget)]

    def __str__(self):
        h = self.hierarchy
        n = len(list(str(h)))
        if self.chosen.value_example:
            return "%s%s: %s" % ('.'*n, self.chosen.text_chosen, self.chosen.value_example)
        else:
            return "%s%s" % ('.'*n, self.chosen.text_chosen)

class OperatedField(ClusterableModel):
    # register_api_chosen = ParentalManyToManyField("RegisterAPIChosen", related_name='api_chosen', blank=True)
    register_api_chosen = ParentalManyToManyField("RegisterAPIChosen", blank=True)
    FIELD_CHOICES = [
        ("Booleanfield", "BooleanField"),
        ("Charfield", "CharField"),
        ("Datefield", "DateField"),
        ("Datetimefield", "DateTimeField"),
        ("Emailfield", "EmailField"),
        ("Filepathfield", "FilePathField"),
        ("Floatfield", "FloatField"),
        ("Integerfield", "IntegerField"),
        ("Positiveintegerfield", "PositiveIntegerField"),
        ("Textfield", "TextField"),
        ("Timefield", "TimeField"),
        ("Urlfield", "URLField"),
        ("Filefield", "FileField"),
        ("Imagefield", "ImageField"),
        ("Jsonfield", "JSONField"),
        ("Geometrycollectionfield", "GeometryCollectionField"),
        ("Geometryfield", "GeometryField"),
        ("Linestringfield", "LinestringField"),
        ("MultilineStringfield", "MultiLineStringField"),
        ("Multipointfield", "MultiPointField"),
        ("Multipolygonfield", "MultiPolygonField"),
        ("Pointfield", "PointField"),
        ("Polygonfield", "PolygonField"),
    ]

    field_type = models.CharField(
        max_length=23,
        choices=FIELD_CHOICES,
        null=True, blank=True
    )

    OPERATION_CHOICES = [
        ("ADD", "ADD"),
        ("SUBSTRAC", "SUBSTRACT"),
        ("DIVIDE", "DIVIDE"),
        ("MULTIPLY", "MULTIPLY"),
        ("PERCENTAGE", "PERCENTAGE"),
    ]

    operation = models.CharField(
        max_length=10,
        choices=OPERATION_CHOICES,
        null=True, blank=True
    )


class RegisterAPI(ClusterableModel):
    id = models.AutoField(primary_key=True, editable=False)
    api_title = models.TextField(max_length=100)
    city = models.CharField(max_length=250, null=True, blank=True)
    country = models.CharField(max_length=250, null=True, blank=True)
    api_endpoint = models.URLField(null=True, blank=True)
    TYPE_CHOICES = [
        ("NONE", "NONE"),
        ("OSM", "OSM"),
    ]

    api_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        null=True, blank=True
    )
    is_dumb = models.BooleanField(default=False)
    first = models.BooleanField(default=True)
    the_time = models.DateTimeField(auto_now_add=True)
    pagination = models.CharField(max_length=100, default=1)
    pagintation_number = models.PositiveIntegerField(null=True, blank=True)
    once_every = models.PositiveIntegerField(null=True, blank=True)
    sleep = models.PositiveIntegerField(null=True, blank=True)
