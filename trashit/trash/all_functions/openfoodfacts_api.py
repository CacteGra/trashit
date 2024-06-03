import requests
from datetime import datetime, timedelta

from django.utils import timezone
from trash.models import Wrapper, Packaging, TheType


def main(code):

    wrapper, created = Wrapper.objects.get_or_create(code=code)
    if (wrapper.the_time < timezone.now() - timedelta(days=1)) or (not wrapper.the_type.all()):

        # Set the product ID (e.g., 1234567890123) or search query
        product_id = code

        # Construct the API request URL
        url = f"https://world.openfoodfacts.org/api/v0/product/{product_id}"

        # Send the GET request and retrieve the response
        response = requests.get(url)

        # Check if the response was successful (200 OK)
        if response.status_code == 200:
            # Parse the JSON response into a Python dictionary
            product_data = response.json()
            try:
                packagings = product_data['product']["packagings"]
            except KeyError:
                return False
            for packaging in packagings:
                material = packaging['material']
                shape = material = packaging['shape']
                try:
                    packaging = Packaging.objects.get(component=shape)
                except Packaging.DoesNotExist:
                    packaging = Packaging.objects.create(component=shape)
                wrapper.packaging.add(packaging)
                wrapper.save()
                material = material.split(':')[1]
                try:
                    the_type = TheType.objects.get(the_type__iexact=material)
                except TheType.DoesNotExist:
                    the_type = TheType.objects.create(the_type=material)
                packaging.the_type = the_type
                packaging.save()
                #the_type, created = TheType.objects.get_or_create(the_type__iexact=material)


        else:
            print("Error:", response.status_code)
            return False
            
    
    return wrapper.pk
