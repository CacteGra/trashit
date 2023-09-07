from django.contrib.gis.db import models

from wagtail.models import Page
from wagtailmetadata.models import MetadataPageMixin
from wagtail.admin.panels import FieldPanel

from wagtail.snippets.models import register_snippet

class LocationFeature(models.Model):
    feature = models.CharField(max_length=100,blank=True,null=True)

class Location(models.Model):
    source_id = models.CharField(max_length=100)
    geolocation = models.PointField(srid=4326)
    city = models.CharField(max_length=50)
    features = models.ForeignKey(LocationFeature, on_delete=models.SET_NULL, null=True)

@register_snippet
class FeaturePage(models.Model):
    feature = models.CharField(max_length=100,blank=True,null=True)
    panels = [
        FieldPanel('feature'),
    ]
    def __str__(self):
        return self.feature

class Endpoint(models.Model):
    api_endpoint = models.URLField()

class ModelPage(MetadataPageMixin, Page):
    has_top_layer = models.BooleanField(default=False)
    top_layer = models.CharField(max_length=100, null=True, blank=True)
    locations = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    date_time = models.DateTimeField(auto_now_add=True)
    source_id = models.CharField(max_length=250)
    geolocation_x = models.CharField(max_length=250)
    geolocation_y = models.CharField(max_length=250)
    city = models.CharField(max_length=250)
    features = models.ForeignKey(FeaturePage, on_delete=models.SET_NULL, null=True, blank=True)
    api_endpoint = models.URLField()
    email = models.EmailField(null=True, blank=True)

    panels = Page.content_panels + [
        FieldPanel('api_endpoint'),
        FieldPanel('has_top_layer'),
        FieldPanel('top_layer'),
        FieldPanel('source_id'),
        FieldPanel('geolocation_x'),
        FieldPanel('geolocation_y'),
        FieldPanel('city'),
        FieldPanel('features'),
        FieldPanel('email'),
    ]

    def get_absolute_url(self):
        return self.get_url()

    def detail_dictionary(dictionary):
        for i in l.keys():
            if isinstance(l, dict):
                return('dict',i)
            else:
                return('list',0)

    def get_endpoint_detail:
        e = Endpoint.objects.all()
        response = requests.get("{}".format(all_model.api_endpoint))
        d = json.dumps(response.json(), sort_keys=True, indent=4)
        l = json.loads(d)
        h = hierarchy(l)
        s = sorted(h)

        def hierarchy(struct, path=None):
            if isinstance(struct, dict):
                path = path if path else '$'
                return set(
                    child_path
                        for key, obj   in struct.items()
                        for child_path in hierarchy(obj, f'{path}.{key}')
                ).union(
                    [path]
                )
            elif isinstance(struct, list):
                path = f'{path}[]' if path else '$[]'
                return set(
                    child_path
                        for obj        in struct
                        for child_path in hierarchy(obj, path)
                ).union(
                    [path]
                )
            else:
                return [path]


def hierarchy(struct, path=None):
    if isinstance(struct, dict):
        path = path if path else '$'
        return set(
            child_path
                for key, obj   in struct.items()
                for child_path in hierarchy(obj, f'{path}.{key}')
        ).union(
            [path]
        )
    elif isinstance(struct, list):
        path = f'{path}[]' if path else '$[]'
        return set(
            child_path
                for obj        in struct
                for child_path in hierarchy(obj, path)
        ).union(
            [path]
        )
    else:
        return [path]

response = requests.get("https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Public_Service_WebMercator/MapServer/10/query?where=1%3D1&outFields=*&outSR=4326&f=json")
d = json.dumps(response.json(), sort_keys=True, indent=4)
l = json.loads(d)
h = hierarchy(l)
s = sorted(h)

def only_one_item(using_dict):
    one_list_dict = {}
    using_dict = [root for root in s if root != '$.']
    using_dict = [root for root in s if root != '$']
    for i in using_dict:
        if '[]' in i:
            i = i.replace('[]','[0]')
        if i == '$':
            continue
        else:
            path_list = i.split('.')
            dict_level = l
            add_last_list = None
            in_list = []
            k = path_list[-1]
            if '[0]' in k:
                dict_level = dict_level[k.replace('[0]', '')]
                one_list_dict[k.replace('[0]', '') = dict_level
                add_last_list = k
                in_list = True
                only_one_item(sorted(hierarchy(dict_level[0]))
            else:
                dict_level = dict_level[k]
                one_list_dict[k] = dict_level


print(one_list_dict)
