"""Reminders App Models"""

from django.db import models
from apps.files.models import ManagedFile


class FileReminder(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('cancelled', 'Cancelled'),
        ('skipped', 'Skipped – File Already Retrieved'),
    ]

    file = models.OneToOneField(ManagedFile, on_delete=models.CASCADE, related_name='reminder')
    scheduled_for = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    job_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    triggered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Reminder for {self.file.file_name} at {self.scheduled_for}"

    class Meta:
        verbose_name = "File Reminder"
        verbose_name_plural = "File Reminders"
        ordering = ['scheduled_for']
