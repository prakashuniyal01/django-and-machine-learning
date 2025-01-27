from rest_framework import serializers
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import DoctorProfile, PatientProfile, CustomUser, Specialization, PasswordResetOTP
from django.core.exceptions import ValidationError
import re
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

# ======================================== doctor specializtions ===============================================
class SpecializationSerializer(serializers.ModelSerializer):
    """
    Serializer for Specialization model.
    """
    class Meta:
        model = Specialization
        fields = ['id', 'name']

#  =================================================== doctor proflie ===================================
    
class DoctorProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for DoctorProfile with specializations.
    Accepts a list of specialization names and handles their creation.
    """
    specializations = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        write_only=True,
        help_text="List of specializations (names)."
    )
    specialization_details = SpecializationSerializer(
        source='specializations', 
        many=True,
        read_only=True,
        help_text="List of specialization objects (read-only)."
    )

    class Meta:
        model = DoctorProfile
        fields = [
            'license_number',
            'specializations',
            'specialization_details',
            'years_experience',
            'clinic_name',
            'clinic_address',
        ]

    def create(self, validated_data):
        doctor_data = validated_data.pop('doctor_profile', None)
        patient_data = validated_data.pop('patient_profile', None)

        # Create user with hashed password
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        # Create DoctorProfile if role=doctor
        if user.role == 'doctor' and doctor_data:
            specializations = doctor_data.pop('specializations', [])
            doctor_profile = DoctorProfile.objects.create(user=user, **doctor_data)
            
            # Handle specializations
            specialization_objects = []
            for spec_name in specializations:
                specialization, _ = Specialization.objects.get_or_create(name=spec_name)
                specialization_objects.append(specialization)
            doctor_profile.specializations.set(specialization_objects)

        # Create PatientProfile if role=patient
        if user.role == 'patient' and patient_data:
            PatientProfile.objects.create(user=user, **patient_data)

        return user


    def update(self, instance, validated_data):
        specializations_data = validated_data.pop('specializations', None)
        doctor_profile = super().update(instance, validated_data)

        if specializations_data is not None:
            # Clear existing specializations and re-add
            doctor_profile.specializations.clear()
            for spec_name in specializations_data:
                specialization, created = Specialization.objects.get_or_create(name=spec_name.strip())
                doctor_profile.specializations.add(specialization)

        return doctor_profile

# ========================================== patient registations ====================================================
class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = ['insurance_details', 'medical_history', 'emergency_contact']

# ====================================================== user registations ============================================
class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Registers a user. If role='doctor', create DoctorProfile;
    if role='patient', create PatientProfile.
    """
    doctor_profile = DoctorProfileSerializer(required=False)
    patient_profile = PatientProfileSerializer(required=False)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'phone',
            'fullname',
            'gender',
            'date_of_birth',
            'address',
            'bio',
            'profile_photo',
            'role',
            'doctor_profile',
            'patient_profile',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'role': {'required': True},
        }

    def validate_role(self, value):
        """Ensure only doctor or patient is accepted; no direct admin creation."""
        if value not in ['doctor', 'patient']:
            raise serializers.ValidationError("Role must be 'doctor' or 'patient'.")
        return value

    def create(self, validated_data):
        doctor_data = validated_data.pop('doctor_profile', None)
        patient_data = validated_data.pop('patient_profile', None)

        # Create user with hashed password using create_user or set_password
        password = validated_data.pop('password')
        try:
            user = User.objects.create_user(**validated_data)
        except IntegrityError as e:
            raise serializers.ValidationError({"detail": str(e)})

        user.set_password(password)
        user.save()

        # Create DoctorProfile if role=doctor
        if user.role == 'doctor' and doctor_data:
            specializations = doctor_data.pop('specializations', [])
            try:
                doctor_profile = DoctorProfile.objects.create(user=user, **doctor_data)
                for spec_name in specializations:
                    specialization, created = Specialization.objects.get_or_create(name=spec_name.strip())
                    doctor_profile.specializations.add(specialization)
            except IntegrityError as e:
                user.delete()  # Cleanup the created user if profile fails
                raise serializers.ValidationError({"detail": str(e)})

        # Create PatientProfile if role=patient
        if user.role == 'patient' and patient_data:
            try:
                PatientProfile.objects.create(user=user, **patient_data)
            except IntegrityError as e:
                user.delete()
                raise serializers.ValidationError({"detail": str(e)})

        return user

# ======================================== user login =============================================================
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Use the custom authentication method to check email and password
        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")
        
        attrs['user'] = user
        return attrs

    def get_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def get_user_details(self, user):
        """Return full user details."""
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'phone': user.phone,
            'gender': user.gender,
            'date_of_birth': user.date_of_birth,
            'address': user.address,
            'bio': user.bio,
            'profile_photo': user.profile_photo,
        }
    


# ========================================== user update ===========================================

class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user details. Allows updating both user and profile information.
    """
    doctor_profile = DoctorProfileSerializer(required=False)
    patient_profile = PatientProfileSerializer(required=False)

    class Meta:
        model = User
        fields = [
            'fullname',  # Include fullname in the fields
            'email',
            'password',
            'phone',
            'gender',
            'date_of_birth',
            'address',
            'bio',
            'profile_photo',
            'doctor_profile',
            'patient_profile',
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'email': {'required': True},
        }

    def validate_role(self, value):
        """Ensure only doctor or patient is accepted."""
        if value not in ['doctor', 'patient']:
            raise serializers.ValidationError("Role must be 'doctor' or 'patient'.")
        return value

    def update(self, instance, validated_data):
        # Update User fields
        instance.fullname = validated_data.get('fullname', instance.fullname)  # Update fullname
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        instance.address = validated_data.get('address', instance.address)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.profile_photo = validated_data.get('profile_photo', instance.profile_photo)

        # If password is provided, update it
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)

        instance.save()

        # Handle profile updates based on role
        doctor_data = validated_data.get('doctor_profile', None)
        if doctor_data and instance.role == 'doctor':
            specializations_data = doctor_data.pop('specializations', None)
            doctor_profile = instance.doctor_profile  # Get the existing doctor profile

            # Update doctor profile fields
            for attr, value in doctor_data.items():
                setattr(doctor_profile, attr, value)
            doctor_profile.save()

            # Handle specializations update
            if specializations_data is not None:
                doctor_profile.specializations.clear()  # Clear existing specializations
                for spec_name in specializations_data:
                    specialization, created = Specialization.objects.get_or_create(name=spec_name.strip())
                    doctor_profile.specializations.add(specialization)

        # Handle patient profile updates
        patient_data = validated_data.get('patient_profile', None)
        if patient_data and instance.role == 'patient':
            patient_profile = instance.patient_profile  # Get the existing patient profile
            for attr, value in patient_data.items():
                setattr(patient_profile, attr, value)
            patient_profile.save()

        return instance


# ================================= change password serializer ======================================

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate_new_password(self, value):
        """
        Validate the new password to ensure it is strong and meets all requirements.
        """
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        
        if not re.search(r'[\!@#\$%\^&\*\(\)_\+\-=\[\]\{\};:\'",<>\./?]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        
        return value

    def validate(self, attrs):
        """
        Ensure the new password and confirm password match.
        """
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("New password and confirm password do not match.")
        return attrs


# ======================================================= reset password ========================================

class PasswordResetOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8)

    def validate_otp(self, value):
        email = self.initial_data.get('email')
        try:
            otp_obj = PasswordResetOTP.objects.get(user__email=email, otp=value, is_verified=False)
            if otp_obj.is_expired():
                raise serializers.ValidationError("OTP has expired. Please request a new one.")
            return value
        except PasswordResetOTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP.")
        

# ============================================ user details ==============================================
class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomUser to display user details including their doctor profile.
    """
    doctor_profile = DoctorProfileSerializer(read_only=True)  # Nested serializer for doctor profile
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'phone', 'gender', 'date_of_birth', 
            'address', 'bio', 'profile_photo', 'role', 'doctor_profile'
        ]

# ============================================ user details ==============================================
class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer to fetch user details including nested profiles for doctors and patients.
    """
    doctor_profile = DoctorProfileSerializer(read_only=True)  # Nested doctor profile
    patient_profile = PatientProfileSerializer(read_only=True)  # Nested patient profile

    class Meta:
        model = User
        fields = [
            'id',  # User ID
            'username',
            'email',
            'phone',
            'fullname',
            'gender',
            'date_of_birth',
            'address',
            'bio',
            'profile_photo',
            'role',
            'doctor_profile',
            'patient_profile',
        ]
