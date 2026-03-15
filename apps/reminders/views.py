"""Reminders Views"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import FileReminder


@login_required
def reminder_list(request):
    reminders = FileReminder.objects.select_related('file', 'file__uploaded_by').filter(
        file__uploaded_by=request.user
    )
    paginator = Paginator(reminders, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'page_title': 'File Reminders',
    }
    return render(request, 'reminders/reminder_list.html', context)
