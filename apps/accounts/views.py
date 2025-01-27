from rest_framework import generics, status
from rest_framework.response import Response
from django.db import DatabaseError
from rest_framework.exceptions import ValidationError
from .serializers import UserRegistrationSerializer, LoginSerializer, UserUpdateSerializer, ChangePasswordSerializer, PasswordResetOTPSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
import logging
from rest_framework.views import APIView
from .models import PasswordResetOTP
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets
from .models import CustomUser
from .serializers import CustomUserSerializer

# Initialize logger
logger = logging.getLogger(__name__)

User = get_user_model()

# ====================================== register view ==================================================
class RegisterView(generics.CreateAPIView):
    """
    Single-step registration endpoint for doctors or patients.
    """
    serializer_class = UserRegistrationSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
        except ValidationError as val_err:
            # Specific validation errors
            logger.error(f"Validation error during registration: {val_err}")
            return Response({"detail": val_err.detail}, status=status.HTTP_400_BAD_REQUEST)
        except DatabaseError as db_err:
            # Database-specific errors
            logger.error(f"Database error during registration: {db_err}")
            return Response({"detail": f"Database error: {str(db_err)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as ex:
            # Catch-all for any other exceptions
            logger.error(f"Unexpected error during registration: {ex}")
            return Response({"detail": f"An unexpected error occurred: {str(ex)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {
                "message": "User registered successfully.",
                "user_id": user.id,
                "role": user.role,
                "username": user.username,
            },
            status=status.HTTP_201_CREATED
        )

# ========================================== login view ===============================================
class LoginView(APIView):
    """
    API for user login using email and password.
    Returns access and refresh tokens along with user details.
    """
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            tokens = serializer.get_tokens(user)
            user_details = serializer.get_user_details(user)
            
            return Response({
                'message': 'Login successful.',
                'tokens': tokens,
                'user': user_details,
            }, status=status.HTTP_200_OK)
        
        except serializers.ValidationError as ve:
            return Response({'detail': ve.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({'detail': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ========================================== doctor profile view ===============================================
class DoctorProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet to retrieve details for doctors including their user and doctor profile information.
    """
    queryset = CustomUser.objects.filter(role='doctor')  # Only fetch users with role "doctor"
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned doctor profiles
        by filtering against a 'doctor_id' query parameter in the URL.
        """
        queryset = super().get_queryset()
        doctor_id = self.request.query_params.get('doctor_id', None)
        if doctor_id:
            queryset = queryset.filter(id=doctor_id)
        return queryset   
# ========================================= update view =========================================

class UserUpdateView(APIView):
    """
    Update user profile, doctor profile, or patient profile.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def put(self, request, user_id, *args, **kwargs):
        user = self.get_object(user_id)
        if user is None:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the requesting user has permission to update the profile
        if request.user.id != user.id:
            return Response({"detail": "You do not have permission to update this user."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserUpdateSerializer(user, data=request.data, partial=False)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "User updated successfully.",
                    "user_id": user.id,
                    "username": user.username,
                    "role": user.role,
                    "fullname": user.fullname,  # Return updated fullname
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, user_id, *args, **kwargs):
        user = self.get_object(user_id)
        if user is None:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the requesting user has permission to update the profile
        if request.user.id != user.id:
            return Response({"detail": "You do not have permission to update this user."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserUpdateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "User updated successfully.",
                    "user_id": user.id,
                    "username": user.username,
                    "role": user.role,
                    "fullname": user.fullname,  # Return updated fullname
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


# ================================ change password view =======================================

class ChangePasswordView(APIView):
    """
    API endpoint to change the password of a user.
    Requires the user to be authenticated.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Handles the change password functionality.
        Validates old password and updates the new password.
        """
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            # Get the current user
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            
            # Authenticate user with the old password
            if not user.check_password(old_password):
                return Response(
                    {"detail": "Old password is incorrect."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update the password
            user.set_password(new_password)
            user.save()
            
            return Response(
                {"detail": "Password changed successfully."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )


# ================================ otp validations ==================================

class RequestPasswordResetOTPView(generics.CreateAPIView):
    """
    Sends an OTP to the user's email for password reset.
    """
    serializer_class = PasswordResetOTPSerializer

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            otp_obj, created = PasswordResetOTP.objects.get_or_create(user=user)

            if not created:
                # If OTP exists, generate a new one
                otp_obj.generate_otp()
            
            otp_obj.send_otp_email()
            return Response({"message": "OTP sent to email."}, status=status.HTTP_200_OK)
        
        except ObjectDoesNotExist:
            return Response({"detail": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(generics.UpdateAPIView):
    """
    Resets the user's password using the OTP.
    """
    serializer_class = PasswordResetOTPSerializer
    queryset = User.objects.all()

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = request.data.get('email')
            otp = request.data.get('otp')
            new_password = request.data.get('new_password')

            # Validate OTP
            try:
                otp_obj = PasswordResetOTP.objects.get(user__email=email, otp=otp, is_verified=False)
                if otp_obj.is_expired():
                    return Response({"detail": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)
                
                # Reset password
                user = otp_obj.user
                user.set_password(new_password)
                user.save()

                # Mark OTP as verified
                otp_obj.is_verified = True
                otp_obj.save()

                return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)

            except PasswordResetOTP.DoesNotExist:
                return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    




    