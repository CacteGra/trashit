import requests
from datetime import datetime, timedelta

from django.utils import timezone
from trash.models import Wrapper, Packaging, TheType


def main(code):

    wrapper, created = Wrapper.objects.get_or_create(code=code)
    if (wrapper.the_time < timezone.now() - timedelta(days=1)) or wrapper.packaging.all().count() == 0:

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
                material = packaging['material'].split(':')[1]
                shape = packaging['shape'].split(':')[1]
                try:
                    packaging = Packaging.objects.get(component=shape)
                except Packaging.DoesNotExist:
                    packaging = Packaging.objects.create(component=shape)
                wrapper.packaging.add(packaging)
                wrapper.save()
                try:
                    the_type = TheType.objects.get(the_type__iexact=material)
                except TheType.DoesNotExist:
                    the_type = TheType.objects.create(the_type=material)
                packaging.the_type = the_type
                packaging.save()
        else:
            print("Error:", response.status_code)
            return False

    return wrapper.pk
