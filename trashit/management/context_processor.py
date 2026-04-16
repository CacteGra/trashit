from .models import PageStats, VisitorSession
from django.utils import timezone
import uuid

def visitor_stats(request):
    if not hasattr(request, 'session'):
        return {}

    # Determine Session ID
    if request.user.is_authenticated:
        session_id = f"user_{request.user.id}"
    else:
        session_id = request.session.session_key or str(uuid.uuid4())

    # 1. Initialize start time in session if not present
    if 'visit_start_time' not in request.session:
        request.session['visit_start_time'] = timezone.now().isoformat()

    # 2. Check if this session is already tracked
    is_new_visitor = not VisitorSession.objects.filter(session_key=session_id).exists()
    
    if is_new_visitor:
        # Record the session
        VisitorSession.objects.create(session_key=session_id)
        
        # Increment the global counter
        stats, created = PageStats.objects.get_or_create(page_name="trash_map")
        stats.total_visitors += 1
        stats.save()

    # 3. Get current total count
    try:
        stats = PageStats.objects.get(page_name="trash_map")
        count = stats.total_visitors
    except PageStats.DoesNotExist:
        count = 0

    # 4. Return context data
    return {
        'visitor_count': count,
        'visit_start_time': request.session.get('visit_start_time'),
    }