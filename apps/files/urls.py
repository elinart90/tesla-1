"""Files App URLs"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.file_list, name='file_list'),
    path('files/upload/', views.file_upload, name='file_upload'),
    path('files/<int:pk>/', views.file_detail, name='file_detail'),
    path('files/<int:pk>/retrieve/', views.file_retrieve, name='file_retrieve'),
    path('files/<int:pk>/delete/', views.file_delete, name='file_delete'),
]
