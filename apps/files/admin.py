"""Admin configuration for Files App"""

from django.contrib import admin
from .models import ManagedFile, FileRetrievalLog, FileCategory, UserProfile


@admin.register(FileCategory)
class FileCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']


class FileRetrievalLogInline(admin.TabularInline):
    model = FileRetrievalLog
    extra = 0
    readonly_fields = ['retrieved_by', 'retrieved_at', 'ip_address']
    can_delete = False


@admin.register(ManagedFile)
class ManagedFileAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'short_id', 'uploaded_by', 'status', 'file_type', 'file_size_display', 'upload_date', 'reminder_sent']
    list_filter = ['status', 'file_type', 'reminder_sent', 'upload_date', 'category']
    search_fields = ['file_name', 'description', 'tags', 'file_id']
    readonly_fields = ['file_id', 'upload_date', 'last_retrieved', 'retrieval_count']
    inlines = [FileRetrievalLogInline]
    date_hierarchy = 'upload_date'


@admin.register(FileRetrievalLog)
class FileRetrievalLogAdmin(admin.ModelAdmin):
    list_display = ['file', 'retrieved_by', 'retrieved_at', 'ip_address']
    list_filter = ['retrieved_at']
    readonly_fields = ['file', 'retrieved_by', 'retrieved_at', 'ip_address']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'phone_number', 'employee_id', 'receive_email', 'receive_sms']
    search_fields = ['user__username', 'user__email', 'department', 'employee_id']
