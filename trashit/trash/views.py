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
        trash_id = request.POST['id']
        t = TrashSpecificities.objects.get(id=trash_id)
        t.photo = request.POST['picture']
        t.save()

        return JsonResponse({"status": "ok"})


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
