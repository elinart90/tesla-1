"""
Files App Models - VRA File Management System
"""

import uuid
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Extended user profile for VRA staff"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    receive_sms = models.BooleanField(default=True)
    receive_email = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.department}"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


class FileCategory(models.Model):
    """File categories/types for classification"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "File Category"
        verbose_name_plural = "File Categories"


class ManagedFile(models.Model):
    """Core file model - stores file metadata"""

    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('retrieved', 'Retrieved'),
        ('expired', 'Expired'),
        ('archived', 'Archived'),
    ]

    file_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    file_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    file_size = models.PositiveBigIntegerField(default=0, help_text="Size in bytes")
    file_type = models.CharField(max_length=50)
    category = models.ForeignKey(FileCategory, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    upload_date = models.DateTimeField(auto_now_add=True)
    last_retrieved = models.DateTimeField(null=True, blank=True)
    retrieval_count = models.PositiveIntegerField(default=0)
    reminder_sent = models.BooleanField(default=False)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.file_name} [{self.file_id}]"

    def file_size_display(self):
        """Human-readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    @property
    def short_id(self):
        return str(self.file_id)[:8].upper()

    class Meta:
        verbose_name = "Managed File"
        verbose_name_plural = "Managed Files"
        ordering = ['-upload_date']


class FileRetrievalLog(models.Model):
    """Audit log for every file retrieval"""
    file = models.ForeignKey(ManagedFile, on_delete=models.CASCADE, related_name='retrieval_logs')
    retrieved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    retrieved_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.file.file_name} - {self.retrieved_by} - {self.retrieved_at}"

    class Meta:
        verbose_name = "File Retrieval Log"
        verbose_name_plural = "File Retrieval Logs"
        ordering = ['-retrieved_at']
