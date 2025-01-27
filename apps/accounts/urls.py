# apps/accounts/urls.py

from django.urls import path
from .views import RegisterView,DoctorProfileViewSet,UserProfileView, LoginView, UserUpdateView, ChangePasswordView, RequestPasswordResetOTPView, PasswordResetView, SpecializationListView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('login/', LoginView.as_view(), name='login'),
    path('<int:user_id>/update/', UserUpdateView.as_view(), name='user-update'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('request-password-reset/', RequestPasswordResetOTPView.as_view(), name='request-password-reset'),
    path('reset-password/', PasswordResetView.as_view(), name='reset-password'),
    path('doctors/', DoctorProfileViewSet.as_view({'get': 'list'}), name='doctor-profile-list'),  # For listing doctor profiles
    path('doctors/<int:pk>/', DoctorProfileViewSet.as_view({'get': 'retrieve'}), name='doctor-profile-detail'),  # For retrieving a single doctor profile
    path('specializations/', SpecializationListView.as_view(), name='specialization-list'),
]
