from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),  # ✅ HERE
    path(
        'analysis/<int:analysis_id>/',
        views.analysis_detail,
        name='analysis_detail'
    ),
    path('download-pdf/', views.download_pdf, name='download_pdf'),
]