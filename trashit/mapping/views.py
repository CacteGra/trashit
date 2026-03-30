from django.template.loader import render_to_string
from django.http import JsonResponse
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.core.serializers import serialize
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import random
from pytz import utc
import numpy as np

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from django.shortcuts import redirect

from datapop.models import Pointfield, OperatedField, RequestLocalWaste
from trash.models import TrashSpecificities, TrashType, TheType, TrashSpecificities
from .forms import RequestLocalForm

class MainPageView(LoginRequiredMixin, TemplateView):
    template_name = 'mapping/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trash_types'] = TheType.objects.values_list('the_type', flat=True).distinct()
        context['all_icons'] = [c[0] for c in TheType.icon.field.choices]
        context['form'] = RequestLocalForm()
        return context

class BaseLoadView(LoginRequiredMixin, ListView):
    model = Pointfield
    login_url = '/admin/'
    redirect_field_name = 'redirect_to'
    
    def distribute_points(self, latlng, num_points):
        lat = latlng.y
        lng = latlng.x
        angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
        points = [(np.cos(angle), np.sin(angle)) for angle in angles]
        return points
    
    def spread(self, types_count, latlng):
        num_points = types_count
        evenly_distributed_points = self.distribute_points(latlng, num_points)
        lat = latlng.y
        lng = latlng.x
        lngs = [(((x[0]*100)/2)*0.000144)/100+(lng) for x in evenly_distributed_points]
        lats = [(((x[1]*100)/2)*0.000144)/100+(lat) for x in evenly_distributed_points]
        return lngs, lats
    
    def iterate_points(self, ts, all_types, not_local_type, request):
        response = []
        type_count_dict = {}
        
        for t in ts:
            data_list = []
            current_types = t.trash_type.all().values('the_type__pk', 'the_type__the_type', 'the_type__icon')
            types_count = current_types.count()
            
            if types_count == 1:
                lngs, lats = [t.point_field.o_field.x], [t.point_field.o_field.y]
            else:
                lngs, lats = self.spread(types_count, t.point_field.o_field)
            
            n = -1
            for current_type in current_types:
                n += 1
                
                # Skip if too many of same type
                try:
                    type_count_dict[current_type['the_type__pk']] += 1
                    if type_count_dict[current_type['the_type__pk']] > 10 and types_count == 1:
                        continue
                except KeyError:
                    type_count_dict[current_type['the_type__pk']] = 1
                
                # Check if type is OSM
                type_is_osm = TheType.objects.filter(osm_type__pk__in=[current_type['the_type__pk']])
                if not type_is_osm and current_type['the_type__the_type'] not in not_local_type:
                    not_local_type.append(current_type['the_type__the_type'])
                
                all_types.append(current_type['the_type__pk'])
                trash_type = current_type['the_type__the_type']
                html = render_to_string('trash/trash-presentation.html', 
                                       {'trash': t, 'trash_type': trash_type}, 
                                       request=request)
                trash_icon = current_type['the_type__icon']
                data_list.append({
                    'html': html, 
                    'lat': lats[n], 
                    'lng': lngs[n], 
                    'trash_id': t.id, 
                    'trash_type': trash_type, 
                    'trash_icon': trash_icon
                })
            
            if data_list:
                response.append({
                    'lng': t.point_field.o_field.x, 
                    'lat': t.point_field.o_field.y, 
                    'radius': 30, 
                    'data_list': data_list
                })
        
        return response, all_types, not_local_type

class FirstLoad(BaseLoadView):
    def get(self, request, *args, **kwargs):
        lat = float(request.GET['lat'])
        lng = float(request.GET['lng'])
        point = Point(lng, lat, srid=4326)
        m = 1000
        all_types = []
        not_local_type = []
        whole_response = []
        
        # Get trashes from local api
        ts = TrashSpecificities.objects.filter(
            point_field__o_field__distance_lte=(point, D(m=m)), 
            from_local_api=True
        ).annotate(distance=Distance("point_field__o_field", point)).order_by("distance")

        if ts:
            admin_email = ts[0].point_field.register_api_chosen.register_api_foreign.admin_mail
        else:
            admin_email = None
        
        response, local_types, not_local_type = self.iterate_points(ts, all_types, not_local_type, request)
        all_types = list(set().union(all_types, local_types))
        whole_response.extend(response)
        
        # Get trashes that are not in local api
        osm_linked_trashes = TrashSpecificities.objects.filter(
            point_field__o_field__distance_lte=(point, D(m=m)), 
            osm_trash_spec__isnull=False, 
            from_local_api=True
        )
        ts = TrashSpecificities.objects.filter(
            point_field__o_field__distance_lte=(point, D(m=m)), 
            osm_trash_spec__isnull=True, 
            from_local_api=False
        ).exclude(pk__in=list(osm_linked_trashes.values_list('osm_trash_spec__pk', flat=True))).annotate(distance=Distance("point_field__o_field", point)).order_by("distance")
        
        response, types, not_local_type = self.iterate_points(ts, all_types, not_local_type, request)
        all_types = list(set().union(all_types, types))
        whole_response.extend(response)
        
        if not whole_response:
            r = RequestLocalWaste.objects.filter(coordinates__distance_lte=(point, D(m=2000)))
            if r:
                whole_response = {'requestlocal': render_to_string('trash/request-local-no-data.html', request=request)}
            else:
                whole_response = {'requestlocal': render_to_string('trash/request-local.html', 
                                                                 {'form': RequestLocalForm(request.POST), 'coordinates': point}, 
                                                                 request=request)}
        else:
            all_types = list(TheType.objects.filter(pk__in=all_types).values_list('the_type', flat=True))
            whole_response = {'response': whole_response, 'all_types': all_types, 'all_icons': [c[0] for c in TheType.icon.field.choices], 'administration_email': admin_email}
        
        return JsonResponse(whole_response, safe=False)

class FilterType(BaseLoadView):
    def get(self, request, *args, **kwargs):
        lat = float(request.GET['lat'])
        lng = float(request.GET['lng'])
        get_type = request.GET['type']
        point = Point(lng, lat, srid=4326)
        whole_response = []
        not_local_type = []
        
        the_type = TheType.objects.get(the_type=get_type)
        trash_types = TrashType.objects.filter(the_type__in=[the_type])
        ts = TrashSpecificities.objects.filter(
            point_field__o_field__distance_lte=(point, D(m=2000)), 
            trash_type__in=trash_types
        ).annotate(distance=Distance("point_field__o_field", point)).order_by("distance")
        whole_response, _, _ = self.iterate_points(ts, [get_type], not_local_type, request)
        
        return JsonResponse(whole_response, safe=False)

class RequestLocal(LoginRequiredMixin, FormView):
    template_name = "trash/request-local.html"
    form_class = RequestLocalForm
    success_url = "/"
    
    def form_valid(self, form):
        RequestLocalWaste.objects.get_or_create(coordinates=form.cleaned_data['coordinates'])
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.warning(self.request, "Form validation failed. Please check your input.")
        return redirect(self.success_url)