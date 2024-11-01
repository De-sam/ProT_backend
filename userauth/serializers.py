# userauth/serializers.py

from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from algosdk import account, mnemonic

User = get_user_model()

class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, help_text="Enter the new password.")
    confirm_password = serializers.CharField(write_only=True, help_text="Re-enter the new password for confirmation.")

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        validate_password(data['new_password'])
        return data

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="User's registered email for password reset.")

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user is associated with this email address.")
        return value

class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, help_text="Password for the new user.")
    password2 = serializers.CharField(write_only=True, help_text="Re-enter the password to confirm.")
    role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES, default=CustomUser.CUSTOMER, help_text="Role of the user, either Tailor or Customer.")
    wallet_address = serializers.CharField(read_only=True, help_text="Algorand wallet address for transactions.")

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2', 'role', 'wallet_address']
        extra_kwargs = {
            'first_name': {'help_text': "User's first name."},
            'last_name': {'help_text': "User's last name."},
            'email': {'help_text': "User's email address for account registration."}
        }

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        validate_password(data['password1'])
        return data

    def create(self, validated_data):
        # Remove confirm password from validated data
        validated_data.pop('password2')
        password = validated_data.pop('password1')

        # Generate Algorand account
        private_key, wallet_address = account.generate_account()
        mnemonic_phrase = mnemonic.from_private_key(private_key)

        # Create the user
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.wallet_address = wallet_address  # Set Algorand wallet address
        user.algorand_private_key = private_key  # Securely store the private key
        user.is_active = False  # Mark as inactive until email confirmation
        user.save()

        # Generate activation link
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_url = f"{settings.SITE_URL}{reverse('account_activation', kwargs={'uidb64': uid, 'token': token})}"

        # Send activation email
        send_mail(
            subject="Activate your account",
            message=f"Click the link to activate your account: {activation_url}\n\nYour Algorand mnemonic for backup: {mnemonic_phrase}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
        )

        return user

    def get_mnemonic_phrase(self, obj):
        # Retrieve the mnemonic phrase temporarily set during creation
        return getattr(obj, 'mnemonic_phrase', None)
