from django.contrib import admin
from .models import FileReminder


@admin.register(FileReminder)
class FileReminderAdmin(admin.ModelAdmin):
    list_display = ['file', 'scheduled_for', 'status', 'triggered_at', 'created_at']
    list_filter = ['status', 'scheduled_for']
    readonly_fields = ['created_at', 'triggered_at', 'job_id']
