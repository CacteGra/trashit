import json
import re
import base64
from django.shortcuts import render
from django.template.loader import render_to_string

from django.views import generic
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from wagtail.admin.views.generic.chooser import  ChooseView, ChooseResultsView, ChooseResultsViewMixin, CreationFormMixin, BaseChooseView
from wagtail.admin.viewsets.chooser import ChooserViewSet

from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from django.template.response import TemplateResponse


from datapop.models import Pointfield
from .models import TrashSpecificities

import re
from pprint import pprint

# Create your views here.

class ReportTrash(LoginRequiredMixin, generic.DetailView):
    model = User
    context_object_name = 'user'
    def post(self, request, *arg, **kwargs):
        print(self.request.POST)
        print(request.POST)
        if request.method == 'POST':
            response_json = request.POST
            response_json = json.dumps(response_json)
            data = json.loads(response_json)
            trash_id = data['id']
            dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
            ImageData = data['imageBase64']
            ImageData = dataUrlPattern.match(ImageData).group(2)
            if (ImageData == None or len(ImageData) == 0):
                pass
            ImageData = base64.b64decode(ImageData)
            trash_image = ContentFile(ImageData, name='trash-image-' + str(id))
            trash = TrashSpecificities.objects.get(id=trash_id)
            trash.photo = trash_image
            trash.save()
            data = {'status': 'Reported'}
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

class GarbageCollection(LoginRequiredMixin, ListView):
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
        collection_area = CollectArea.objects.get(polygon_field__o_field__contains=point)
        print(collection_area)
        html = ""
        print(collection_area.trashtype_set.all().count())
        if collection_area:
            html = render_to_string('trash/collection-days.html', {'collections': collection_area.trashtype_set.all()}, request=request)
        else:
            html = render_to_string('trash/zero-collection-days.html', {'collections': collection_area.trashtype_set.all()}, request=request)
        print(html)
        return JsonResponse([{'html': html}], safe=False)

class ScanWrapper(LoginRequiredMixin, ListView):
    from trash.models import Wrapper
    model = Wrapper
    login_url = '/admin/'
    redirect_field_name = 'redirect_to'
    def get(self, request, *arg, **kwargs):
        from django.contrib.gis.geos import Point
        from trash.models import Wrapper
        from .all_functions import openfoodfacts_api
        code = int(request.GET['code'])
        pk = openfoodfacts_api.main(code)
        wrapper = Wrapper.objects.get(pk=pk)
        html = render_to_string('trash/packaging-bin.html', {'packagings': wrapper.the_type.all()}, request=request)
        print(html)
        return JsonResponse([{'html': html}], safe=False)

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
