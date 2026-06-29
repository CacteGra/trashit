import json
import re
import base64
from django.shortcuts import render
from django.template.loader import render_to_string

from django.views import generic, View
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator

from wagtail.admin.views.generic.chooser import  ChooseView, ChooseResultsView, ChooseResultsViewMixin, CreationFormMixin, BaseChooseView
from wagtail.admin.viewsets.chooser import ChooserViewSet

from django.core.paginator import Paginator
from django.utils import translation
from django.template.response import TemplateResponse


from datapop.models import Pointfield, RegisterAPI
from .models import TrashSpecificities, TrashType, TheType, TypeLocale

import re
from pprint import pprint

# Create your views here.

def get_language(request):
    # Detect language before page load
    user_languages = request.META.get('HTTP_ACCEPT_LANGUAGE', 'en')
    
    # Parse browser languages (like "fr-FR,fr;q=0.9,en;q=0.8")
    languages = []
    if user_languages:
        for lang in user_languages.split(','):
            lang_code = lang.split(';')[0].strip()
            languages.append(lang_code)
    
    # Determine preferred language
    preferred_language = 'en'  # default
    supported_languages = ['en', 'fr', 'es']  # your supported languages
    
    for lang in languages:
        if lang in supported_languages:
            preferred_language = lang
            break
        # Check language codes without region
        lang_code = lang.split('-')[0]
        if lang_code in supported_languages:
            preferred_language = lang_code
            break
    return preferred_language

class ReportTrash(generic.DetailView):
    model = User
    context_object_name = 'user'
    def post(self, request, *arg, **kwargs):
        data = {'status': 'Report failed'}
        if request.method == 'POST':
            response_json = request.POST
            response_json = json.dumps(response_json)
            data = json.loads(response_json)
            identification = data['id'].split(" ")
            point_id = identification[0]
            trash_type = identification[1]
            dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
            ImageData = data['imageBase64']
            ImageData = dataUrlPattern.match(ImageData).group(2)
            if (ImageData == None or len(ImageData) == 0):
                pass
            ImageData = base64.b64decode(ImageData)
            trash_image = ContentFile(ImageData, name='trash-image-' + str(id))
            point = Pointfield.objects.get(id=point_id)
            try:
                locale_type = TypeLocale.objects.get(locale=trash_type)
                spec_type = TrashType.objects.get(the_type=locale_type.the_type, trashspecificities__point_field=point)
                trash = TrashSpecificities.objects.get(trash_type=spec_type, point_field=point)
            except TypeLocale.DoesNotExist:
                the_type = TheType.objects.get(the_type=trash_type)
                spec_type = TrashType.objects.get(the_type=the_type, trashspecificities__point_field=point)
                trash = TrashSpecificities.objects.get(trash_type=spec_type, point_field=point)
            trash.photo = trash_image
            trash.save()
            data = {'status': 'Reported'}
        return JsonResponse(data, safe=False)


class ReportDump(generic.DetailView):
    from django.contrib.auth.models import User
    model = User
    context_object_name = 'user'
    def post(self, request, *arg, **kwargs):
        lat = int(request.POST['lat'])
        lng = int(request.POST['lng'])
        trash_point = Pointfield.objects.get_or_create(o_field=Point(lat,long))
        TrashSpecificities.objects.get_or_create(pointfield=trash_point)
        return True

class GarbageCollection(ListView):
    from trash.models import CollectArea
    model = CollectArea
    login_url = '/admin/'
    redirect_field_name = 'redirect_to'
    def get(self, request, *arg, **kwargs):
        from django.contrib.gis.geos import Point
        from trash.models import CollectArea
        lat = float(request.GET['lat'])
        lng = float(request.GET['lng'])
        print(lat)
        print(lng)
        point = Point(lng, lat, srid=4326)
        print(request)
        preferred_language = get_language(request)
        print(preferred_language)
        translation.activate(preferred_language)
        collect_area_apis = RegisterAPI.objects.filter(api_trash="COLLECTAREA")
        try:
            collection_area = CollectArea.objects.get(polygon_field__o_field__contains=point, polygon_field__register_api_chosen__register_api_foreign__in=collect_area_apis)
        except CollectArea.DoesNotExist:
            collection_area = None
        print(collection_area)
        if collection_area:
            html = render_to_string('trash/collection-days.html', {'collection': collection_area}, request=request)
        else:
            html = render_to_string('trash/zero-collection-days.html', {'collection': collection_area}, request=request)
        print(html)
        return JsonResponse([{'html': html}], safe=False)

class ScanWrapper(ListView):
    from trash.models import Wrapper
    model = Wrapper
    login_url = '/admin/'
    redirect_field_name = 'redirect_to'
    def get(self, request, *arg, **kwargs):
        from django.contrib.gis.geos import Point
        from trash.models import Wrapper
        from .all_functions import openfoodfacts_api
        code = int(request.GET['code'])
        wrapper, available = openfoodfacts_api.main(code)
        html = render_to_string('trash/packaging-bin.html', {'wrapper': wrapper, 'available': available}, request=request)
        return JsonResponse([{'html': html, }], safe=False)

@method_decorator(csrf_protect, name='dispatch')
class CreateTrash(TemplateView):
    def post(self, request, *arg, **kwargs):
        from django.contrib.gis.measure import D
        from django.contrib.gis.db.models.functions import Distance
        from django.contrib.gis.geos import Point
        if request.method != 'POST':
            return JsonResponse({'success': False, 'error': 'Invalid request'}, status=405)
        print(request.POST)
        # try:
        #     data = dict(request.POST)
        #     print(data)
        #     lat = float(data['lat'])
        #     lng = float(data['lng'])
        #     point = Point(lng, lat, srid=4326)
        #     bin_type = data['type']
        #     m = 1

        #     locale_type = TypeLocale.objects.get(locale=bin_type)
        #     spec_types = TrashType.objects.filter(the_type=locale_type.the_type)
        #     trash = TrashSpecificities.objects.filter(trash_type__in=spec_types, point_field__o_field__distance_lte=(point, D(m=m))).annotate(distance=Distance("point_field__o_field", point)).order_by("distance")
        #     if trash:
        #         is_valid = True
        #     else:
        #         is_valid = False
            
        #     if is_valid:
        #         trash = TrashSpecificities.objects.get_or_create(trash_type__in=spec_types, point_field=point, to_validate=True)
        #         return JsonResponse({'success': True, 'message': 'Bin registered.'})
        #     else:
        #         return JsonResponse({'success': False, 'error': 'Location or type invalid.'})
                
        # except Exception as e:
        #     return JsonResponse({'success': False, 'error': str(e)}, status=400)

        data = dict(request.POST)
        print(data)
        lat = float(data['lat'][0])
        lng = float(data['lng'][0])
        point = Point(lng, lat, srid=4326)
        bin_type = int(data['type'][0])
        m = 1

        locale_type = TypeLocale.objects.get(id=bin_type)
        print(locale_type.the_type)
        spec_types = TrashType.objects.filter(the_type=locale_type.the_type)
        trash = TrashSpecificities.objects.filter(trash_type__in=spec_types, point_field__o_field__distance_lte=(point, D(m=m))).annotate(distance=Distance("point_field__o_field", point)).order_by("distance")
        if not trash:
            point_object, created = Pointfield.objects.get_or_create(o_field=point)
            trash, created = TrashSpecificities.objects.get_or_create(point_field=point_object)
            trash.to_validate = True
            trash.save()
            for spec_type in spec_types:
                trash.trash_type.add(spec_type)
            return JsonResponse({'success': True, 'message': 'Bin registered.'})
        else:
            if trash.filter(to_validate=True):
                if trash.point_field__o_field != point:
                    trash.recording_count += 1
                    trash.save()
                return JsonResponse({'success': False, 'error': 'Trash record is being reviewed.'})
            else:
                return JsonResponse({'success': False, 'error': 'Trash with same type already recorded.'})


class IssueChooseView(ChooseView):
    model = "trash.TrashSpecificities"
    per_page = 50

    def get_context_data(self, **kwargs):
        print('inside get_context_data')
        context = super().get_context_data(**kwargs)

        results_url = self.get_results_url()

        # For result pagination links, we need a version of results_url with parameters removed,
        # so that the pagination include can append its own parameters via the {% querystring %} template tag
        results_pagination_url = re.sub(r"\?.*$", "", results_url)

        context.update(
            {
                "results": self.results,
                "table": self.table,
                "results_url": results_url,
                "results_pagination_url": results_pagination_url,
                "is_searching": self.filter_form.is_searching,
                "is_filtering_by_collection": self.filter_form.is_filtering_by_collection,
                "is_multiple_choice": self.is_multiple_choice,
                "search_query": self.filter_form.search_query,
                "can_create": self.can_create(),
            }
        )
        if self.is_multiple_choice:
            context["chosen_multiple_url"] = self.get_chosen_multiple_url()
        return context

    def filter_object_list(self, objects):
        print(self.request)
        if self.construct_queryset_hook_name:
            # allow hooks to modify the queryset
            for hook in hooks.get_hooks(self.construct_queryset_hook_name):
                objects = hook(objects, self.request)
                print(objects.count())
                objects = objects.filter(reported=True)
        if self.filter_form.is_valid():
            objects = self.filter_form.filter(objects)
            print(objects.count())
            objects = objects.filter(reported=True)
            print(objects.count())
        return objects

    def get_results_page(self, request):
        objects = self.get_object_list()
        objects = self.apply_object_list_ordering(objects)
        objects = self.filter_object_list(objects)
        print('gonna paginate')
        paginator = Paginator(objects, per_page=self.per_page)
        try:
            return paginator.page(request.GET.get("p", 1))
        except InvalidPage:
            raise Http404

class IssueResultsView(ChooseResultsViewMixin, CreationFormMixin, BaseChooseView):
    def filter_object_list(self, objects):
        if self.construct_queryset_hook_name:
            # allow hooks to modify the queryset
            for hook in hooks.get_hooks(self.construct_queryset_hook_name):
                objects = hook(objects, self.request)
                print(objects.count())
                objects = objects.filter(reported=True)
                print(objects.count())
        if self.filter_form.is_valid():
            objects = self.filter_form.filter(objects)
            print(objects.count())
            objects = objects.filter(reported=True)
            print(objects.count())
        return objects

    def get_results_page(self, request):
        objects = self.get_object_list()
        objects = self.apply_object_list_ordering(objects)
        objects = self.filter_object_list(objects)
        print('gonna paginate')
        paginator = Paginator(objects, per_page=self.per_page)
        try:
            return paginator.page(request.GET.get("p", 1))
        except InvalidPage:
            raise Http404
    pass


class IssueChooserViewSet(ChooserViewSet):
    # The model can be specified as either the model class or an "app_label.model_name" string;
    # using a string avoids circular imports when accessing the StreamField block class (see below)
    model = "trash.TrashSpecificities"
    choose_view_class = IssueChooseView
    choose_results_view_class = IssueResultsView

    per_page = 50

    icon = "view"
    choose_one_text = "Map"

issue_chooser_viewset = IssueChooserViewSet("issue_chooser")
