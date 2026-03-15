"""
Dashboard Views - VRA File Management System
Includes Power BI embed token generation
"""

import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse

from apps.files.models import ManagedFile, FileRetrievalLog
from apps.notifications.models import Notification
from apps.reminders.models import FileReminder

logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    """Main dashboard with system statistics"""
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)

    # File statistics
    total_files = ManagedFile.objects.filter(is_active=True).count()
    uploaded_today = ManagedFile.objects.filter(
        is_active=True, upload_date__date=now.date()
    ).count()
    retrieved_files = ManagedFile.objects.filter(is_active=True, status='retrieved').count()
    pending_files = ManagedFile.objects.filter(is_active=True, status='uploaded').count()
    overdue_reminders = FileReminder.objects.filter(status='scheduled', scheduled_for__lte=now).count()

    # Recent files
    recent_files = ManagedFile.objects.filter(
        is_active=True
    ).select_related('uploaded_by', 'category').order_by('-upload_date')[:8]

    # Recent retrieval logs
    recent_retrievals = FileRetrievalLog.objects.select_related(
        'file', 'retrieved_by'
    ).order_by('-retrieved_at')[:8]

    # Files by status (chart data)
    status_data = list(
        ManagedFile.objects.filter(is_active=True)
        .values('status')
        .annotate(count=Count('id'))
    )

    # Uploads per day (last 7 days)
    uploads_per_day = []
    for i in range(6, -1, -1):
        day = now.date() - timedelta(days=i)
        count = ManagedFile.objects.filter(
            is_active=True, upload_date__date=day
        ).count()
        uploads_per_day.append({'date': day.strftime('%d %b'), 'count': count})

    # Notification stats
    total_notifications = Notification.objects.filter(user=request.user).count()
    failed_notifications = Notification.objects.filter(status='failed').count()

    context = {
        'page_title': 'Dashboard',
        'total_files': total_files,
        'uploaded_today': uploaded_today,
        'retrieved_files': retrieved_files,
        'pending_files': pending_files,
        'overdue_reminders': overdue_reminders,
        'recent_files': recent_files,
        'recent_retrievals': recent_retrievals,
        'status_data': status_data,
        'uploads_per_day': uploads_per_day,
        'total_notifications': total_notifications,
        'failed_notifications': failed_notifications,
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def powerbi_report(request):
    """Power BI embedded report view"""
    from django.conf import settings
    embed_token = None
    embed_url = None
    error = None

    try:
        embed_token, embed_url = _get_powerbi_embed_token()
    except Exception as e:
        error = str(e)
        logger.error(f"Power BI token error: {e}")

    context = {
        'page_title': 'Power BI Reports',
        'embed_token': embed_token,
        'embed_url': embed_url,
        'report_id': settings.POWERBI_REPORT_ID,
        'powerbi_error': error,
    }
    return render(request, 'dashboard/powerbi_report.html', context)


def _get_powerbi_embed_token():
    """
    Obtain Power BI embed token using Azure AD client credentials flow.
    Returns (embed_token, embed_url) tuple.
    """
    import urllib.request
    import urllib.parse
    import json
    from django.conf import settings

    tenant_id = settings.POWERBI_TENANT_ID
    client_id = settings.POWERBI_CLIENT_ID
    client_secret = settings.POWERBI_CLIENT_SECRET
    workspace_id = settings.POWERBI_WORKSPACE_ID
    report_id = settings.POWERBI_REPORT_ID

    # Step 1: Get Azure AD access token
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_data = urllib.parse.urlencode({
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://analysis.windows.net/powerbi/api/.default',
    }).encode('utf-8')

    token_req = urllib.request.Request(token_url, data=token_data, method='POST')
    with urllib.request.urlopen(token_req) as resp:
        token_resp = json.loads(resp.read())
    access_token = token_resp['access_token']

    # Step 2: Get embed token from Power BI REST API
    embed_token_url = (
        f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}"
        f"/reports/{report_id}/GenerateToken"
    )
    embed_data = json.dumps({'accessLevel': 'View'}).encode('utf-8')
    embed_req = urllib.request.Request(
        embed_token_url,
        data=embed_data,
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        },
        method='POST'
    )
    with urllib.request.urlopen(embed_req) as resp:
        embed_resp = json.loads(resp.read())

    embed_token = embed_resp['token']
    embed_url = (
        f"https://app.powerbi.com/reportEmbed"
        f"?reportId={report_id}&groupId={workspace_id}"
    )
    return embed_token, embed_url
