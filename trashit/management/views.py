from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from .models import VisitorStats, PageStats

from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


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

@csrf_exempt # We use exempt because sendBeacon can be tricky with CSRF tokens
@require_POST
def record_time_spent(request):
    duration = request.POST.get('duration')
    page_name = request.POST.get('page_name')

    if duration and page_name:
        try:
            stats = PageStats.objects.get(page_name=page_name)
            stats.total_seconds_spent += int(duration)
            stats.save()
            return HttpResponse("OK", status=200)
        except PageStats.DoesNotExist:
            # Create if doesn't exist
            PageStats.objects.create(
                page_name=page_name, 
                total_seconds_spent=int(duration),
                total_visitors=1
            )
            return HttpResponse("Created", status=201)
            
    return HttpResponse("Invalid Data", status=400)