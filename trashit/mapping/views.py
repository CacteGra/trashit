from django.template.loader import render_to_string

# Create your views here.
from django.http import JsonResponse
from django.core.serializers import serialize
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import FormView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin

class MainPageView(LoginRequiredMixin, TemplateView):
    template_name = 'mapping/home.html'
    def get_context_data(self, **kwargs):
        from trash.models import TheType

        from .forms import RequestLocalForm

        context = super(MainPageView, self).get_context_data(**kwargs)
        context['trash_types'] = TheType.objects.values_list('the_type', flat=True).distinct()
        context['form'] = RequestLocalForm()
        return context


class FirstLoad(LoginRequiredMixin, ListView):
    from datapop.models import Pointfield
    model = Pointfield
    login_url = '/admin/'
    redirect_field_name = 'redirect_to'

    def iterate_points(self, ts, all_types, not_local_type, request):
        from trash.models import TheType
        response = []
        type_count_dict = {}
        for t in ts:
            data_list = []
            # Gather all types of current local api trash 
            current_types = t.trash_type.all().values('the_type__pk', 'the_type__the_type', 'the_type__icon')
            # Generate coordinates for each type icon
            n = -1
            types_count = current_types.count()
            if types_count == 1:
                lngs, lats = [t.point_field.o_field.x], [t.point_field.o_field.y]
            else:
                lngs, lats = self.spread(types_count, t.point_field.o_field)
            # Create trash html and add it to list with trash info
            for current_type in current_types:
                print(type_count_dict)
                # Ignore remaining trash type found if more
                try:
                    type_count_dict[current_type['the_type__pk']] += 1
                    if type_count_dict[current_type['the_type__pk']] > 5:
                        continue
                except KeyError:
                    type_count_dict[current_type['the_type__pk']] = 1
                type_is_osm = TheType.objects.filter(osm_type__pk__in=[current_type['the_type__pk']])
                if not type_is_osm and current_type['the_type__the_type'] not in not_local_type:
                    not_local_type.append(current_type['the_type__the_type'])
                all_types.append(current_type['the_type__pk'])
                html = None
                n += 1
                trash_type = current_type['the_type__the_type']
                html = render_to_string('trash/trash-presentation.html', {'trash': t, 'trash_type': trash_type}, request=request)
                trash_icon = current_type['the_type__icon']
                data_list.append({'html': html, 'lat': lats[n], 'lng': lngs[n], 'trash_id': t.id, 'trash_type': trash_type, 'trash_icon': trash_icon})
            if data_list:
                response.append({'lng': t.point_field.o_field.x, 'lat': t.point_field.o_field.y, 'radius': 30, 'data_list': data_list})
                print(t.distance)
        return response, all_types, not_local_type

    def distribute_points(self, latlng, num_points):
        import numpy as np
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

    def get(self, request, *arg, **kwargs):
        from django.contrib.gis.geos import Point
        from django.contrib.gis.measure import D
        from django.contrib.gis.db.models.functions import Distance
        from django.core.exceptions import ObjectDoesNotExist
        from django.db.models import Q

        from datetime import datetime, timedelta
        import random
        from pytz import utc

        from datapop.models import OperatedField, Pointfield, RequestLocalWaste
        from trash.models import TrashSpecificities, TrashType, TheType

        from .forms import RequestLocalForm

        lat = float(request.GET['lat'])
        lng = float(request.GET['lng'])
        point = Point(lng, lat, srid=4326)
        no_repeat_closest_trash = None
        whole_response = []
        m = 500
        all_types = []
        local_types = None
        not_local_type = []
        response_types = []
        # Get trashes from local api
        ts = TrashSpecificities.objects.filter(point_field__o_field__distance_lte=(point,D(m=m)),from_local_api=True).annotate(distance=Distance("point_field__o_field", point)).order_by("distance")
        response, local_types, not_local_type = self.iterate_points(ts, all_types, not_local_type, request)
        all_types = list(set().union(all_types, local_types))
        whole_response.extend(response)
        tt = ts
        # Get trashes that are not in local api, by way of querying osm trashes that are not found in trashspecificities osm_trash_spec field
        osm_linked_trashes = TrashSpecificities.objects.filter(point_field__o_field__distance_lte=(point,D(m=m)),osm_trash_spec__isnull=False,from_local_api=True)
        ts = TrashSpecificities.objects.filter(point_field__o_field__distance_lte=(point,D(m=m)),osm_trash_spec__isnull=True,from_local_api=False).exclude(pk__in=list(osm_linked_trashes.values_list('osm_trash_spec__pk', flat=True))).annotate(distance=Distance("point_field__o_field", point)).order_by("distance")
        the_types = TheType.objects.filter(pk__in=all_types)
        exclude_done = TrashType.objects.filter(the_type__in=the_types)
        ts = ts.exclude(trash_type__in=exclude_done)
        response, types, not_local_type = self.iterate_points(ts, all_types, not_local_type, request)
        response_types.extend(not_local_type)
        all_types = list(set().union(all_types, types))
        whole_response.extend(response)
        # Get trashes with rest of types within x km that are from local api
        tt.union(TrashType.objects.filter(the_type__pk__in=types))
        ts = TrashSpecificities.objects.filter(point_field__o_field__distance_lte=(point,D(m=2000)),from_local_api=True).annotate(distance=Distance("point_field__o_field", point)).order_by("distance")
        ts = ts.exclude(trash_type__pk__in=tt.values_list('pk', flat=True))
        the_types = TheType.objects.filter(pk__in=all_types)
        exclude_done = TrashType.objects.filter(the_type__in=the_types)
        ts = ts.exclude(trash_type__in=exclude_done)
        tt.union(ts)
        response, types, not_local_type = self.iterate_points(ts, all_types, not_local_type, request)
        all_types = list(set().union(all_types, types))
        whole_response.extend(response)
        # Get trashes with rest of types within x km that are left osm trashes
        tt.union(TrashType.objects.filter(the_type__pk__in=types))
        osm_linked_trashes = TrashSpecificities.objects.filter(point_field__o_field__distance_lte=(point,D(m=2000)),osm_trash_spec__isnull=False,from_local_api=True)
        ts = TrashSpecificities.objects.filter(point_field__o_field__distance_lte=(point,D(m=1000)),osm_trash_spec__isnull=True,from_local_api=False).exclude(pk__in=list(osm_linked_trashes.values_list('osm_trash_spec__pk', flat=True))).annotate(distance=Distance("point_field__o_field", point)).order_by("distance")
        ts = ts.exclude(trash_type__pk__in=tt.values_list('pk', flat=True))
        tt.union(ts)
        the_types = TheType.objects.filter(pk__in=all_types)
        exclude_done = TrashType.objects.filter(the_type__in=the_types)
        ts = ts.exclude(trash_type__in=exclude_done)
        response, types, not_local_type = self.iterate_points(ts, all_types, not_local_type, request)
        response_types.extend(not_local_type)
        all_types = list(set().union(all_types, types))
        whole_response.extend(response)
        all_types = list(TheType.objects.filter(pk__in=all_types).values_list('the_type', flat=True))    
        response_types.extend(list(TheType.objects.filter(pk__in=local_types).values_list('the_type', flat=True)))
        if not whole_response:
            r = RequestLocalWaste.objects.filter(coordinates__distance_lte=(point,D(m=2000)))
            if r:
                whole_response = {'requestlocal': render_to_string('trash/request-local-no-data.html', request=request)}
            else:
                whole_response = {'requestlocal': render_to_string('trash/request-local.html', { 'form': RequestLocalForm(request.POST), 'coordinates': point}, request=request)}
        else:
            whole_response = {'response': whole_response, 'all_types': response_types}
        return JsonResponse(whole_response, safe=False)

class FilterType(LoginRequiredMixin, ListView):
    from datapop.models import Pointfield
    model = Pointfield
    login_url = '/admin/'
    redirect_field_name = 'redirect_to'

    def iterate_points(self, ts, all_types, request):
        response = []
        for t in ts:
            data_list = []
            # Gather all types of current local api trash 
            current_types = t.trash_type.all().values('the_type__pk', 'the_type__the_type', 'the_type__icon')
            # Generate coordinates for each type icon
            n = -1
            types_count = current_types.count()
            if types_count == 1:
                lngs, lats = [t.point_field.o_field.x], [t.point_field.o_field.y]
            else:
                lngs, lats = self.spread(types_count, t.point_field.o_field)
            # Create trash html and add it to list with trash info
            for current_type in current_types:
                all_types.append(current_type['the_type__pk'])
                html = None
                n += 1
                trash_type = current_type['the_type__the_type']
                html = render_to_string('trash/trash-presentation.html', {'trash': t, 'trash_type': trash_type}, request=request)
                trash_icon = current_type['the_type__icon']
                data_list.append({'html': html, 'lat': lats[n], 'lng': lngs[n], 'trash_id': t.id, 'trash_type': trash_type, 'trash_icon': trash_icon})
            response.append({'lng': t.point_field.o_field.x, 'lat': t.point_field.o_field.y, 'radius': 30, 'data_list': data_list})
        return response, all_types

    def distribute_points(self, latlng, num_points):
        import numpy as np
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

    def get(self, request, *arg, **kwargs):
        from django.contrib.gis.geos import Point
        from django.contrib.gis.measure import D
        from django.contrib.gis.db.models.functions import Distance
        from django.core.exceptions import ObjectDoesNotExist
        from django.db.models import Q

        from datetime import datetime, timedelta
        import random
        from pytz import utc

        from datapop.models import OperatedField, Pointfield
        from trash.models import TrashSpecificities, TrashType, TheType

        lat = float(request.GET['lat'])
        lng = float(request.GET['lng'])
        get_type = request.GET['type']
        print(get_type)
        print(lat)
        print(lng)
        point = Point(lng, lat, srid=4326)
        no_repeat_closest_trash = None
        whole_response = []
        m = 500
        all_types = []
        if get_type == 'all':
            # Get trashes from local api
            ts = TrashSpecificities.objects.filter(point_field__o_field__distance_lte=(point,D(m=m)),from_local_api=True)
            response, types = self.iterate_points(ts, all_types, request)
            all_types = list(set().union(all_types, types))
            whole_response.extend(response)
            # Get trashes that are not in local api, by way of querying osm trashes that are not found in trashspecificities osm_trash_spec field
            osm_linked_trashes = TrashSpecificities.objects.filter(point_field__o_field__distance_lte=(point,D(m=m)),osm_trash_spec__isnull=False,from_local_api=True)
            print(list(osm_linked_trashes.values_list('osm_trash_spec__pk', flat=True)))
            ts = TrashSpecificities.objects.filter(point_field__o_field__distance_lte=(point,D(m=m)),osm_trash_spec__isnull=True,from_local_api=False).exclude(pk__in=list(osm_linked_trashes.values_list('osm_trash_spec__pk', flat=True)))
            print(ts.values_list('pk', flat=True))
            response, types = self.iterate_points(ts, all_types, request)
            all_types = list(set().union(all_types, types))
            whole_response.extend(response)
            # Get trashes with rest of types within 1 km that are from local api
            tt = TrashType.objects.filter(the_type__pk__in=all_types)
            ts = TrashSpecificities.objects.filter(point_field__o_field__distance_lte=(point,D(m=1000)),from_local_api=True)
            ts = ts.exclude(trash_type__pk__in=tt.values_list('pk', flat=True))
            response, types = self.iterate_points(ts, all_types, request)
            all_types = list(set().union(all_types, types))
            whole_response.extend(response)
            # Get trashes with rest of types within 1 km that are left osm trashes
            print(all_types)
            tt = TrashType.objects.filter(the_type__pk__in=all_types)
            print(tt.count())
            osm_linked_trashes = TrashSpecificities.objects.filter(point_field__o_field__distance_lte=(point,D(m=1000)),osm_trash_spec__isnull=False,from_local_api=True)
            ts = TrashSpecificities.objects.filter(point_field__o_field__distance_lte=(point,D(m=1000)),osm_trash_spec__isnull=True,from_local_api=False).exclude(pk__in=list(osm_linked_trashes.values_list('osm_trash_spec__pk', flat=True)))
            print(ts.count())
            ts = ts.exclude(trash_type__pk__in=tt.values_list('pk', flat=True))
            print(ts.count())
            response, types = self.iterate_points(ts, all_types, request)
            all_types = list(set().union(all_types, types))
            whole_response.extend(response)
        else:
            the_type = TheType.objects.get(the_type=get_type)
            trash_types = TrashType.objects.filter(the_type__in=[the_type])
            ts = TrashSpecificities.objects.filter(point_field__o_field__distance_lte=(point,D(m=m)),trash_type__in=trash_types)
            while not ts and m < 2000:
                m += 250
                ts = TrashSpecificities.objects.filter(point_field__o_field__distance_lte=(point,D(m=m)),trash_type__in=trash_types)
            whole_response, types = self.iterate_points(ts, all_types, request)
        return JsonResponse(whole_response, safe=False)


class RequestLocal(LoginRequiredMixin, FormView):
    from .forms import RequestLocalForm

    template_name = "trash/request-local.html"
    form_class = RequestLocalForm
    success_url = "/"

    def form_valid(self, form):
        from datapop.models import RequestLocalWaste
        print(form.cleaned_data)
        RequestLocalWaste.objects.get_or_create(coordinates=form.cleaned_data['coordinates'])
        return super().form_valid(form)

    def form_invalid(self, form):
        from django.http import HttpResponseRedirect
        print("FAILED")
        return HttpResponseRedirect('/')