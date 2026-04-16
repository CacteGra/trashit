from .models import VisitorStats
from django.utils import timezone
import uuid

def visitor_stats(request):
    if request.user.is_authenticated:
        # Use user ID to track unique users
        session_id = f"user_{request.user.id}"
    else:
        # Use session key for anonymous users
        if not hasattr(request, 'session'):
            return {}
        session_id = request.session.session_key or str(uuid.uuid4())

    # Check if this session has already been counted
    try:
        stats = VisitorStats.objects.get(page_name="trash_map", session_key=session_id)
    except VisitorStats.DoesNotExist:
        # New visitor: Increment global count and save session
        VisitorStats.objects.update_or_create(
            page_name="trash_map",
            session_key=session_id, # This session is now 'counted'
            defaults={'total_visitors': VisitorStats.objects.filter(page_name="trash_map").aggregate(models.Sum('total_visitors'))}
        )
        # For simplicity in this example, we just increment a counter
        # A real production app might use Redis or a more complex atomic increment
        VisitorStats.objects.filter(page_name="trash_map").update(total_visitors=models.F('total_visitors') + 1)
        # Initialize the start time in the session
        request.session['visit_start_time'] = timezone.now().isoformat()

    try:
        # Fetch the latest global count
        global_stats = VisitorStats.objects.filter(page_name="trash_map").order_by('-total_visitors').first()
        count = global_stats.total_visitors if global_stats else 0
    except:
        count = 0

    # Get the stored start time
    start_time = request.session.get('visit_start_time')

    return {
        'visitor_count': count,
        'visit_start_time': start_time,
    }