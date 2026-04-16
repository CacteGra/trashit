from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from .models import VisitorStats, PageStats

@method_decorator(staff_member_required, name='dispatch')
class VisitorStatsView(TemplateView):
    template_name = 'admin/visitor_stats.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the main page statistics
        stats = VisitorStats.objects.filter(page_name="trash_map").first()
        context['visitor_count'] = stats.total_visitors if stats else 0
        context['stats'] = VisitorStats.objects.all().order_by('-created_at')[:10]
        return context