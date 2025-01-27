from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Appointment
from .serializers import AppointmentSerializer, AppointmentStatusSerializer

class AppointmentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'doctor':
            return Appointment.objects.filter(doctor=user)
        elif user.role == 'patient':
            return Appointment.objects.filter(patient=user)
        return Appointment.objects.none()

    def perform_create(self, serializer):
        # Automatically set patient from request
        serializer.save(patient=self.request.user)

class AppointmentStatusUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentStatusSerializer
    queryset = Appointment.objects.all()

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.doctor != request.user:
            return Response(
                {"detail": "You are not authorized to update this appointment."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().patch(request, *args, **kwargs)
