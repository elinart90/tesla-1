"""Forms for Files App"""

from django import forms
from .models import ManagedFile, FileCategory
from django.conf import settings


class FileUploadForm(forms.ModelForm):
    file_name = forms.CharField(
        required=False,
        label="File Name (optional)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Leave blank to use original filename'
        })
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description of file content...'})
    )
    category = forms.ModelChoiceField(
        queryset=FileCategory.objects.all(),
        required=False,
        empty_label="-- Select Category --",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. report, invoice, 2024 (comma separated)'
        })
    )
    file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.jpg,.jpeg,.png,.zip'})
    )

    class Meta:
        model = ManagedFile
        fields = ['file_name', 'file', 'category', 'description', 'tags']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            ext = file.name.split('.')[-1].lower()
            allowed = getattr(settings, 'ALLOWED_FILE_TYPES', [])
            if allowed and ext not in allowed:
                raise forms.ValidationError(f"File type '.{ext}' is not allowed. Allowed types: {', '.join(allowed)}")
            max_size = getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 52428800)
            if file.size > max_size:
                raise forms.ValidationError(f"File size exceeds the maximum allowed size of {max_size // 1048576} MB.")
        return file


class FileSearchForm(forms.Form):
    STATUS_CHOICES = [('', 'All Statuses')] + list(ManagedFile.STATUS_CHOICES)

    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, ID, tag...'
        })
    )
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    category = forms.ModelChoiceField(
        queryset=FileCategory.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
