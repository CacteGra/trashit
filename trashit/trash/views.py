import json

from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from datapop.models import Pointfield
from .models import TrashSpecificities

# Create your views here.

class ReportTrash(LoginRequiredMixin, generic.DetailView):
    from django.contrib.auth.models import User
    from django.http import JsonResponse
    from django.views.decorators.csrf import csrf_exempt
    import base64
    import os
    model = User
    context_object_name = 'user'
    def post(self, request, *arg, **kwargs):
        if request.method == 'POST':
            response_json = request.POST
            response_json = json.dumps(response_json)
            data = json.loads(response_json)

            print(data['imageBase64'])


        return JsonResponse(data, safe=False)


class ReportDump(LoginRequiredMixin, generic.DetailView):
    from django.contrib.auth.models import User
    model = User
    context_object_name = 'user'
    def post(self, request, *arg, **kwargs):
        lat = int(request.POST['lat'])
        lng = int(request.POST['lng'])
        trash_point = Pointfield.objects.get_or_create(o_field=Point(lat,long))
        TrashSpecificities.objects.get_or_create(pointfield=trash_point)
        return True
