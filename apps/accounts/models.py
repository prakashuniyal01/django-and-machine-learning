from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator, EmailValidator
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
import random


class CustomUserManager(BaseUserManager):
    """
    Custom manager for CustomUser with proper role handling.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set.")
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create a superuser with the role of admin.
        """
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('role', 'admin')  # Ensure the role is admin
        if extra_fields.get('role') != 'admin':
            raise ValueError('Superuser must have role as "admin".')
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Custom user model with additional fields like role and phone.
    """
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(
        unique=True,
        validators=[EmailValidator(message="Invalid email format.")]
    )
    phone_validator = RegexValidator(regex=r'^\d+$', message="Phone number must contain digits only.")
    phone = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        validators=[phone_validator],
        help_text="Enter digits only."
    )
    fullname = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    gender = models.CharField(max_length=10, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_photo = models.URLField(blank=True, null=True, help_text="Store a URL or relative path.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Ensure staff and superuser roles are handled
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    class Meta:
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["phone"]),
        ]

    def save(self, *args, **kwargs):
        if self.role not in ['doctor', 'patient', 'admin']:
            raise ValueError("Invalid role. Must be 'doctor', 'patient', or 'admin'.")
        # Automatically set is_staff for admin users
        if self.role == 'admin':
            self.is_staff = True
            self.is_superuser = True
        super().save(*args, **kwargs)


class Specialization(models.Model):
    """
    Specializations table for doctors.
    """
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class DoctorProfile(models.Model):
    """
    Additional fields only for Doctors.
    One-to-one relationship with CustomUser.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='doctor_profile')
    license_number = models.CharField(max_length=100, unique=True)
    specializations = models.ManyToManyField(Specialization, related_name='doctors')
    years_experience = models.PositiveIntegerField(default=0)
    clinic_name = models.CharField(max_length=255, blank=True, null=True)
    clinic_address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"DoctorProfile: {self.user.fullname}"


class PatientProfile(models.Model):
    """
    Additional fields only for Patients.
    One-to-one relationship with CustomUser.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='patient_profile')
    insurance_details = models.CharField(max_length=255, blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(
        max_length=20, blank=True, null=True,
        validators=[RegexValidator(regex=r'^\d+$', message="Emergency contact must contain digits only.")]
    )

    def __str__(self):
        return f"PatientProfile: {self.user.fullname}"


class PasswordResetOTP(models.Model):
    """
    OTP for password reset.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))  # Generate 6-digit OTP
        self.save()

    def is_expired(self):
        expiration_time = self.created_at + timedelta(minutes=10)  # OTP expires in 10 minutes
        return timezone.now() > expiration_time

    def send_otp_email(self):
        """
        Send OTP email to the user.
        """
        send_mail(
            'Password Reset OTP',
            f'Your OTP for password reset is {self.otp}',
            'from@example.com',
            [self.user.email],
            fail_silently=False,
        )
