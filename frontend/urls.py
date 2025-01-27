from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('doctorprofile/', views.doctorprofile, name='doctorprofile'),
    path('doctor-profile/', views.profile, name='doctor-profile'),
    path('patientprofile/', views.patientprofile, name='patientprofile'),
]