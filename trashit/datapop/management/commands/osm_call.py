from datapop.models import RegisterAPI, Pointfield
from trash.models import TrashSpecificities, TrashType, TheType
from django.contrib.gis.geos import Point
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass
import time
import logging

logger = logging.getLogger(__name__)

def safe_overpass_query(query, max_retries=3, delay=5):
    overpass = Overpass()
    for attempt in range(max_retries):
        try:
            result = overpass.query(query)
            return result
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
    raise Exception("Failed to execute Overpass query after retries") from e


def main(api_pk):
    register_api = RegisterAPI.objects.get(pk=api_pk)
    nominatim = Nominatim()

    areaId = nominatim.query(f"{register_api.city}, {register_api.state}, {register_api.country}").areaId()
    queries = [
        ("waste_basket", 'amenity="waste_basket"'),
        ("waste_disposal", 'amenity="waste_disposal"'),
        ("recycling", 'amenity="recycling"')
    ]

    icon_mapping = {
        'plastic': 'plasticbottle',
        'paper': 'paper',
        'magazines': 'paper',
        'shoes': 'shirt',
        'clothes': 'shirt',
        'cans': 'can',
        'cardboard': 'cardboard',
        'glass': 'glassbottle',
        'oil': 'specialbin',
    }

    # Process each amenity type
    for amenity_name, selector in queries:
        query = overpassQueryBuilder(area=areaId, elementType='node', selector=selector, out='body')
        result = safe_overpass_query(query)
        elements = result.elements()

        for i in elements:
            point = Point(i.lon(), i.lat(), srid=4326)
            point_field, created = Pointfield.objects.get_or_create(
                o_field=point,
                register_api_chosen__isnull=True,
                data_line__isnull=True
            )

            d = i.tags()
            waste_type = d.get('waste', 'trash')
            type_list = []

            if ";" in waste_type:
                waste_types = [w.strip() for w in waste_type.split(";")]
            else:
                waste_types = [waste_type]

            for wt in waste_types:
                the_type, created = TheType.objects.get_or_create(
                    the_type=wt,
                    is_osm=True
                )

                # Only set icon if newly created and match icon
                if created:
                    icon = icon_mapping.get(wt, 'specialbin' if not any(x in wt for x in ['waste', 'trash']) else 'trashicon')
                    the_type.icon = icon
                    the_type.save()

                trash_type, _ = TrashType.objects.get_or_create(the_type=the_type)
                type_list.append(trash_type)

            # Link to TrashSpecificities
            try:
                t = TrashSpecificities.objects.get(point_field=point_field)
                if not t.trash_type.exists():
                    for tt in type_list:
                        t.trash_type.add(tt)
            except TrashSpecificities.DoesNotExist:
                t = TrashSpecificities.objects.create(point_field=point_field)
                for tt in type_list:
                    t.trash_type.add(tt)

    register_api.first = False
    register_api.save()