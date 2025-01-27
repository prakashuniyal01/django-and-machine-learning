from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request, 'home.html')

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

# @login_required
def doctorprofile(request):
    return render(request, 'doctor/dashboard.html')

def profile(request):
    return render(request, 'doctor/profile.html')

# @login_required
def patientprofile(request):
    return render(request, 'patient/dashboard.html')