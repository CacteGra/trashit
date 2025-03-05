import urllib.request, urllib.error
import json
from time import sleep

from django.core.files import File
import kml2geojson


from . import one_list_item

from datapop.models import RegisterAPI, RegisterAPIChosen, Chosen

def main(register_api_pk):

    all_api = RegisterAPI.objects.get(pk=register_api_pk)
    url = all_api.api_endpoint
    n = 0
    while True:
        n += 1
        try:
            response = urllib.request.urlopen(url)
            break
        except urllib.error.URLError:
            if n == 5:
                return False
            sleep(1)
    if all_api.api_type == "KML":
        json_response = kml2geojson.main.convert(response)
    else:
        json_response = json.load(response)
    all_api.register_file.save('json_file.json', File(json_response))
    one_list_item.main(json_response, register_api_pk)