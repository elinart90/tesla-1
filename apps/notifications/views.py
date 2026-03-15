"""Notifications Views"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Notification


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).select_related('file')
    paginator = Paginator(notifications, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'page_title': 'Notifications',
    }
    return render(request, 'notifications/notification_list.html', context)
