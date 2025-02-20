from django.shortcuts import render
from django.views import generic

# Create your views here.

from wagtail.admin.views.generic.chooser import  ChooseView, ChooseViewMixin, ChooseResultsView, ChooseResultsViewMixin, CreationFormMixin, BaseChooseView
from wagtail.admin.viewsets.chooser import ChooserViewSet

from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from django.template.response import TemplateResponse

import re
from pprint import pprint

class ChosenChooserMixin:
    def get_object_list(self):
        registerapi_url = self.request.META['HTTP_REFERER']
        print(registerapi_url)
        registerapi_pk = registerapi_url.split('admin/snippets/datapop/registerapi/edit/')
        registerapi_pk = registerapi_pk[-1].replace('/','')
        print(registerapi_pk)
        objects = self.model_class.objects.all()
        objects = objects.filter(choosing__register_api_foreign__pk=registerapi_pk)
        return objects

class ChosenChooseView(ChosenChooserMixin, ChooseView):
    pass

class ChooseAPIResultsView(ChosenChooserMixin, ChooseResultsView):
    pass

class ChosenChooserViewSet(ChooserViewSet):
    # The model can be specified as either the model class or an "app_label.model_name" string;
    # using a string avoids circular imports when accessing the StreamField block class (see below)
    model = "datapop.Chosen"
    choose_view_class = ChosenChooseView
    choose_results_view_class = ChooseAPIResultsView

    icon = "view"
    choose_one_text = "Choose a key"


chosen_chooser_viewset = ChosenChooserViewSet("chosen_chooser")

class OperatedChooseView(ChooseView):
    model = "datapop.RegisterAPIChosen"
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
                objects = objects.filter(field_type__isnull=False)
                print(objects.count())
                objects = objects.exclude(the_chosen__text_chosen='root')
                print(objects.count())
        if self.filter_form.is_valid():
            objects = self.filter_form.filter(objects)
            print(objects.count())
            objects = objects.filter(field_type__isnull=False)
            print(objects.count())
            objects = objects.exclude(the_chosen__text_chosen='root')
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

class OperatedResultsView(ChooseResultsViewMixin, CreationFormMixin, BaseChooseView):
    def filter_object_list(self, objects):
        if self.construct_queryset_hook_name:
            # allow hooks to modify the queryset
            for hook in hooks.get_hooks(self.construct_queryset_hook_name):
                objects = hook(objects, self.request)
                print(objects.count())
                objects = objects.filter(field_type__isnull=False)
                print(objects.count())
                objects = objects.exclude(the_chosen__text_chosen='root')
                print(objects.count())
        if self.filter_form.is_valid():
            objects = self.filter_form.filter(objects)
            print(objects.count())
            objects = objects.filter(field_type__isnull=False)
            print(objects.count())
            objects = objects.exclude(the_chosen__text_chosen='root')
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

class OperatedChooserViewSet(ChooserViewSet):
    # The model can be specified as either the model class or an "app_label.model_name" string;
    # using a string avoids circular imports when accessing the StreamField block class (see below)
    model = "datapop.RegisterAPIChosen"
    # choose_view_class = OperatedChooseView
    # choose_results_view_class = OperatedResultsView

    per_page = 50

    icon = "view"
    choose_one_text = "Choose a key"


operated_chooser_viewset = OperatedChooserViewSet("operated_chooser")

class TrashTypeChooseView(ChooseView):
    model = "datapop.RegisterAPIChosen"
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
                objects = objects.filter(area=True)
                print(objects.count())
        if self.filter_form.is_valid():
            objects = self.filter_form.filter(objects)
            print(objects.count())
            objects = objects.filter(area=True)
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

class TrashTypeResultsView(ChooseResultsViewMixin, CreationFormMixin, BaseChooseView):
    def filter_object_list(self, objects):
        if self.construct_queryset_hook_name:
            # allow hooks to modify the queryset
            for hook in hooks.get_hooks(self.construct_queryset_hook_name):
                objects = hook(objects, self.request)
                print(objects.count())
                objects = objects.filter(area=True)
                print(objects.count())
        if self.filter_form.is_valid():
            objects = self.filter_form.filter(objects)
            print(objects.count())
            objects = objects.filter(area=True)
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


class TrashTypeChooserViewSet(ChooserViewSet):
    # The model can be specified as either the model class or an "app_label.model_name" string;
    # using a string avoids circular imports when accessing the StreamField block class (see below)
    model = "trash.TrashType"
    # choose_view_class = OperatedChooseView
    # choose_results_view_class = OperatedResultsView

    per_page = 50

    icon = "view"
    choose_one_text = "Choose a key"


trash_type_chooser_viewset = TrashTypeChooserViewSet("trash_type_chooser")