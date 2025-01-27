from rest_framework import serializers
from .models import Appointment
from datetime import date, datetime, timedelta

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['status', 'created_at', 'updated_at']

    def validate(self, data):
        # Ensure patient and doctor roles are valid
        if data['doctor'].role != 'doctor':
            raise serializers.ValidationError("Assigned doctor must have the 'doctor' role.")
        if data['patient'].role != 'patient':
            raise serializers.ValidationError("Booking must be done by a patient.")

        # Ensure the appointment date is not in the past
        if data['appointment_date'] < date.today():
            raise serializers.ValidationError("Appointment cannot be booked for a past date.")

        # If the appointment is today, ensure the time is not in the past
        if data['appointment_date'] == date.today() and data['start_time'] < datetime.now().time():
            raise serializers.ValidationError("Appointment time cannot be in the past.")

        # Ensure the time slot is not already booked
        # Check if any existing appointment overlaps with the requested appointment slot
        overlapping_appointments = Appointment.objects.filter(
            doctor=data['doctor'],
            appointment_date=data['appointment_date'],
            start_time__lt=data['end_time'],  # Check if the start time of any appointment is before the requested end time
            end_time__gt=data['start_time']   # Check if the end time of any appointment is after the requested start time
        )

        if overlapping_appointments.exists():
            raise serializers.ValidationError("The selected time slot is already booked. Please choose a different time.")

        return data


class AppointmentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['status']
