from django.urls import path
from .views import AppointmentListCreateView, AppointmentStatusUpdateView

urlpatterns = [
    path('', AppointmentListCreateView.as_view(), name='appointment-list-create'),
    path('<int:pk>/status/', AppointmentStatusUpdateView.as_view(), name='appointment-status-update'),
]
