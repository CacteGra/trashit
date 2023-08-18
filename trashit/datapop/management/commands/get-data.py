from time import sleep
import requests
import json

from django.core.management.base import BaseCommand, CommandError
from datapop.models import ModelPage, Location
from django.contrib.gis.geos import Point

class Command(BaseCommand):
    help = 'Add or update API data'

    def handle(self, *args, **options):
        print("script ran")
        while True:
            print('in the loop')
            all_models = ModelPage.objects.all()
            for all_model in all_models:
                response = requests.get("{}".format(all_model.api_endpoint))
                d = json.dumps(response.json(), sort_keys=True, indent=4)
                l = json.loads(d)
                if all_model.has_top_layer:
                    l = l[all_model.top_layer]
                geolocation = Point(l[all_model.geolocation_x], l[all_model.geolocation_y], srid=4326)
                location = Location.objects.create(source_id=l[all_model.source_id],geolocation=geolocation,city=l[all_model.source_id])
                location.save()
                all_model.locations = location
                all_model.save()
            # exist_list = []
            # location.objects.filter(modelpage=all_model).exclude(pk__in=[exist_list]).delete()

            sleep(5)




