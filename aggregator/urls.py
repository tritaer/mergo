from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_file, name='upload_file'),
    path('generate-report/', views.generate_commerce_report, name='generate_commerce_report'),
    path('generate-prs/', views.generate_prs_file, name='generate_prs_file'),
]
