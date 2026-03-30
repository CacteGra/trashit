from datapop.models import RegisterAPI, Pointfield
from trash.models import TrashSpecificities, TrashType, TheType
from django.contrib.gis.geos import Point
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass
import time
import logging
import traceback

logger = logging.getLogger(__name__)

def safe_overpass_query(query, max_retries=3, delay=5):
    overpass = Overpass()
    for attempt in range(max_retries):
        try:
            result = overpass.query(query)
            return result
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            logger.debug(f"Full traceback: {traceback.format_exc()}")
            if attempt < max_retries - 1:
                time.sleep(delay)
    raise Exception("Failed to execute Overpass query after retries") from e


def process_amenity_type(amenity_name, selector, areaId, icon_mapping):
    """Process a single amenity type with error handling"""
    try:
        logger.info(f"Processing {amenity_name}...")
        query = overpassQueryBuilder(area=areaId, elementType='node', selector=selector, out='body')
        result = safe_overpass_query(query)
        elements = result.elements()
        
        logger.info(f"Found {len(elements)} {amenity_name} elements")
        
        for i, element in enumerate(elements):
            try:
                # Process each element
                point = Point(element.lon(), element.lat(), srid=4326)
                point_field, created = Pointfield.objects.get_or_create(
                    o_field=point,
                    register_api_chosen__isnull=True,
                    data_line__isnull=True
                )

                d = element.tags()
                type_list = []

                # Handle different amenity types differently
                if amenity_name == "waste_basket":
                    # For waste_basket, get waste type from 'waste' tag
                    waste_type = d.get('waste', 'trash')
                    if ";" in waste_type:
                        waste_types = [w.strip() for w in waste_type.split(";")]
                    else:
                        waste_types = [waste_type]
                        
                elif amenity_name == "waste_disposal":
                    # For waste_disposal, get waste type from 'waste' tag
                    waste_type = d.get('waste', 'trash')
                    if ";" in waste_type:
                        waste_types = [w.strip() for w in waste_type.split(";")]
                    else:
                        waste_types = [waste_type]
                        
                elif amenity_name == "recycling":
                    # For recycling, extract recycling types from tags
                    waste_types = []
                    # Check for specific recycling tags like recycling:plastic, recycling:paper, etc.
                    for key, value in d.items():
                        if key.startswith('recycling:') and value == 'yes':
                            waste_type = key.replace('recycling:', '')
                            if waste_type:
                                waste_types.append(waste_type)
                    
                    # If no specific recycling tags, try to get from name or operator
                    if not waste_types:
                        try:
                            waste_type = d.get('name', d.get('operator', 'recycle'))
                            if waste_type:
                                waste_types = [waste_type]
                        except:
                            waste_types = ['recycle']
                    # If we have recycling tags, we already have the types

                # Process all waste types
                for wt in waste_types:
                    if wt == "":
                        continue
                    try:
                        
                        the_type, created = TheType.objects.get_or_create(
                            the_type=wt,
                            is_osm=True
                        )

                        # Only set icon if newly created and match icon
                        if created:
                            icon = [val for key, val in icon_mapping.items() if key in wt]
                            if icon:
                                icon = icon[0]
                            elif amenity_name == 'recycling' and not icon:
                                icon = 'recycle'
                            else:
                                icon = 'trashicon'
                            # icon = icon_mapping.get(wt, 'specialbin' if not any(x in wt for x in ['waste', 'trash']) else 'trashicon')
                            # Use update() instead of save() to avoid modelcluster issues
                            TheType.objects.filter(pk=the_type.pk).update(icon=icon)

                        trash_type, _ = TrashType.objects.get_or_create(the_type=the_type)
                        type_list.append(trash_type)
                    except Exception as e:
                        logger.error(f"Error processing waste type '{wt}' for {amenity_name}: {e}")
                        logger.debug(f"Full traceback: {traceback.format_exc()}")
                        continue  # Continue with next waste type

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
                except Exception as e:
                    logger.error(f"Error handling TrashSpecificities for {amenity_name}: {e}")
                    logger.debug(f"Full traceback: {traceback.format_exc()}")
                    continue  # Continue with next element

            except Exception as e:
                logger.error(f"Error processing element {i} in {amenity_name}: {e}")
                logger.debug(f"Full traceback: {traceback.format_exc()}")
                continue  # Continue with next element
                
    except Exception as e:
        logger.error(f"Critical error processing {amenity_name}: {e}")
        logger.debug(f"Full traceback: {traceback.format_exc()}")
        return False
    
    return True


def main(api_pk):
    try:
        register_api = RegisterAPI.objects.get(pk=api_pk)
        nominatim = Nominatim()
        logger.info("Starting OSM data processing...")
        
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
            'organic': 'organic',
            'food_waste': 'organic',
            'oil': 'specialbin',
        }

        # Process each amenity type with error handling
        for amenity_name, selector in queries:
            success = process_amenity_type(amenity_name, selector, areaId, icon_mapping)
            if not success:
                logger.error(f"Failed to process {amenity_name}, but continuing...")
                continue

        # Update register_api status
        register_api.first = False
        register_api.save()
        logger.info("Successfully completed OSM data processing")
        
    except Exception as e:
        logger.error(f"Critical failure in main function: {e}")
        logger.debug(f"Full traceback: {traceback.format_exc()}")
        # Don't raise the exception so the script can continue running
        return False
    
    return True
