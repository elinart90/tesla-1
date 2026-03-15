"""
Files App Views - VRA File Management System
"""

import os
import mimetypes
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator

from .models import ManagedFile, FileRetrievalLog, FileCategory, UserProfile
from .forms import FileUploadForm, FileSearchForm
from apps.notifications.services import NotificationService
from apps.reminders.services import ReminderService


@login_required
def file_list(request):
    """List all files with search/filter"""
    form = FileSearchForm(request.GET or None)
    files = ManagedFile.objects.filter(is_active=True).select_related('uploaded_by', 'category')

    if form.is_valid():
        q = form.cleaned_data.get('query')
        status = form.cleaned_data.get('status')
        category = form.cleaned_data.get('category')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')

        if q:
            files = files.filter(
                Q(file_name__icontains=q) |
                Q(description__icontains=q) |
                Q(tags__icontains=q) |
                Q(file_id__icontains=q)
            )
        if status:
            files = files.filter(status=status)
        if category:
            files = files.filter(category=category)
        if date_from:
            files = files.filter(upload_date__date__gte=date_from)
        if date_to:
            files = files.filter(upload_date__date__lte=date_to)

    paginator = Paginator(files, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'form': form,
        'total_files': files.count(),
        'page_title': 'File Repository',
    }
    return render(request, 'files/file_list.html', context)


@login_required
def file_upload(request):
    """Upload a new file"""
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            managed_file = form.save(commit=False)
            managed_file.uploaded_by = request.user
            managed_file.file_name = form.cleaned_data.get('file_name') or uploaded_file.name
            managed_file.file_size = uploaded_file.size
            ext = os.path.splitext(uploaded_file.name)[1].lstrip('.').lower()
            managed_file.file_type = ext
            managed_file.save()

            # Schedule reminder
            ReminderService.schedule_file_reminder(managed_file)

            # Send upload confirmation notification
            NotificationService.send_upload_confirmation(managed_file, request.user)

            messages.success(request, f'File "{managed_file.file_name}" uploaded successfully. File ID: {managed_file.short_id}')
            return redirect('file_detail', pk=managed_file.pk)
    else:
        form = FileUploadForm()

    context = {
        'form': form,
        'page_title': 'Upload File',
    }
    return render(request, 'files/file_upload.html', context)


@login_required
def file_detail(request, pk):
    """View file details"""
    managed_file = get_object_or_404(ManagedFile, pk=pk, is_active=True)
    retrieval_logs = managed_file.retrieval_logs.select_related('retrieved_by').order_by('-retrieved_at')[:10]

    context = {
        'file': managed_file,
        'retrieval_logs': retrieval_logs,
        'page_title': 'File Details',
    }
    return render(request, 'files/file_detail.html', context)


@login_required
def file_retrieve(request, pk):
    """Download/retrieve a file and log the action"""
    managed_file = get_object_or_404(ManagedFile, pk=pk, is_active=True)

    # Log retrieval
    FileRetrievalLog.objects.create(
        file=managed_file,
        retrieved_by=request.user,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

    # Update file status and metadata
    managed_file.last_retrieved = timezone.now()
    managed_file.retrieval_count += 1
    managed_file.status = 'retrieved'
    managed_file.save()

    # Send retrieval notification
    NotificationService.send_retrieval_notification(managed_file, request.user)

    # Serve file
    try:
        file_path = managed_file.file.path
        content_type, _ = mimetypes.guess_type(file_path)
        response = FileResponse(
            open(file_path, 'rb'),
            content_type=content_type or 'application/octet-stream',
            as_attachment=True,
            filename=managed_file.file_name
        )
        return response
    except FileNotFoundError:
        raise Http404("File not found on server.")


@login_required
def file_delete(request, pk):
    """Soft delete a file"""
    managed_file = get_object_or_404(ManagedFile, pk=pk, is_active=True)

    if request.method == 'POST':
        # Only uploader or admin can delete
        if request.user == managed_file.uploaded_by or request.user.is_staff:
            managed_file.is_active = False
            managed_file.save()
            messages.success(request, f'File "{managed_file.file_name}" has been deleted.')
            return redirect('file_list')
        else:
            messages.error(request, 'You do not have permission to delete this file.')

    context = {
        'file': managed_file,
        'page_title': 'Delete File',
    }
    return render(request, 'files/file_confirm_delete.html', context)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')
