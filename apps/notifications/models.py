"""Notifications App Models"""

from django.db import models
from django.contrib.auth.models import User
from apps.files.models import ManagedFile


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('upload_confirm', 'Upload Confirmation'),
        ('retrieval', 'File Retrieved'),
        ('reminder', 'Reminder'),
        ('system', 'System'),
    ]
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('both', 'Both'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    file = models.ForeignKey(ManagedFile, on_delete=models.SET_NULL, null=True, blank=True)
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default='both')
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.user.username} [{self.status}]"

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']
