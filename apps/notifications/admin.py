from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'channel', 'status', 'sent_at', 'created_at']
    list_filter = ['notification_type', 'channel', 'status', 'created_at']
    search_fields = ['user__username', 'subject']
    readonly_fields = ['created_at', 'sent_at']
