# userauth/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import CustomUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.throttling import ScopedRateThrottle
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
import logging
from django.utils import timezone

# Set up the logger
logger = logging.getLogger('django.security')

class CustomLoginView(TokenObtainPairView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user = CustomUser.objects.get(email=email)
            if not user.is_active:
                logger.warning(f"Inactive login attempt: {email} at {timezone.now()}")
                return Response(
                    {"detail": _("Account is not activated. Please check your email for the activation link.")},
                    status=status.HTTP_403_FORBIDDEN
                )

            user = authenticate(request, email=email, password=password)
            if user is not None:
                logger.info(f"Successful login: {email} at {timezone.now()}")
                refresh = RefreshToken.for_user(user)
                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "role": user.role
                }, status=status.HTTP_200_OK)

            logger.warning(f"Failed login attempt (incorrect password): {email} at {timezone.now()}")
            return Response({"detail": _("Invalid credentials.")}, status=status.HTTP_401_UNAUTHORIZED)

        except CustomUser.DoesNotExist:
            logger.warning(f"Failed login attempt (nonexistent account): {email} at {timezone.now()}")
            return Response({"detail": _("Invalid credentials or account does not exist.")}, status=status.HTTP_401_UNAUTHORIZED)

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "This is a protected view only accessible to authenticated users."})


class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = get_object_or_404(CustomUser, email=email)
            token = PasswordResetTokenGenerator().make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )

            send_mail(
                subject="Password Reset Request",
                message=f"Click the link to reset your password: {reset_url}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
            )
            return Response({"message": "Password reset link sent"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            return Response({"error": "Invalid user ID"}, status=status.HTTP_400_BAD_REQUEST)

        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "User created successfully. Please check your email to activate your account.",
                "role": user.role,
                "customer_id": user.customer_id if user.role == CustomUser.CUSTOMER else None,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "wallet_address": user.wallet_address,
                "mnemonic_phrase": user.algorand_private_key  # Send the mnemonic phrase in the response
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AccountActivationView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "Account activated successfully"}, status=status.HTTP_200_OK)
        
        return Response({"error": "Activation link is invalid!"}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "User logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class AddCustomerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Check that the requesting user is a tailor
        if request.user.role != CustomUser.TAILOR:
            return Response({"detail": "Only tailors can add customers."}, status=status.HTTP_403_FORBIDDEN)

        customer_id = request.data.get('customer_id')
        if not customer_id:
            return Response({"detail": "Customer ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Find the customer by customer ID
            customer = CustomUser.objects.get(customer_id=customer_id, role=CustomUser.CUSTOMER)
            
            # Add customer to the tailor's list if not already added
            if customer in request.user.customers.all():
                return Response({"detail": "Customer is already added."}, status=status.HTTP_400_BAD_REQUEST)

            request.user.customers.add(customer)
            return Response({"message": "Customer added successfully."}, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({"detail": "Customer with this ID does not exist."}, status=status.HTTP_404_NOT_FOUND)
