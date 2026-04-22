from django.views.generic import TemplateView

# Create your views here.

class About(TemplateView):
    template_name = 'about/index.html'