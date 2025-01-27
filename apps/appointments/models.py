# appointments/models.py
from django.db import models
from django.utils.timezone import now
from apps.accounts.models import CustomUser

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='doctor_appointments')
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='patient_appointments')
    appointment_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='SCHEDULED')
    reason_for_visit = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_slot_available(self):
        """
        Check if the appointment slot is already booked.
        """
        overlapping_appointments = Appointment.objects.filter(
            doctor=self.doctor,
            appointment_date=self.appointment_date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
            status='SCHEDULED'
        )
        return not overlapping_appointments.exists()
