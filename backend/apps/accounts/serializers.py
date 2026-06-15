from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.conf import settings
import uuid

from .validators import validate_phone, validate_password_strength

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    Used for reading user data.
    """

    wallet_number = serializers.CharField(source='wallet_id.wallet_number', read_only=True, default=None)
    balance = serializers.DecimalField(
        source='wallet_id.balance',
        max_digits=15,
        decimal_places=2,
        read_only=True,
        default=None
    )
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'first_name', 'last_name',
            'full_name', 'role', 'is_verified', 'profile_picture',
            'date_of_birth', 'address', 'city', 'country',
            'wallet_id', 'wallet_number', 'balance',
            'is_active', 'pin_set', 'date_joined', 'last_login'
        ]
        read_only_fields = [
            'id', 'role', 'is_verified', 'wallet_id', 'wallet_number',
            'balance', 'is_active', 'pin_set', 'date_joined', 'last_login'
        ]


class SetPinSerializer(serializers.Serializer):
    """Serializer for setting a transaction PIN (4 digits)."""
    pin = serializers.CharField(
        max_length=4,
        min_length=4,
        write_only=True,
        help_text="4-digit transaction PIN"
    )
    confirm_pin = serializers.CharField(
        max_length=4,
        min_length=4,
        write_only=True,
        help_text="Confirm 4-digit transaction PIN"
    )

    def validate_pin(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('PIN must contain only digits.')
        return value

    def validate(self, attrs):
        if attrs['pin'] != attrs['confirm_pin']:
            raise serializers.ValidationError({'confirm_pin': 'PINs do not match.'})
        return attrs

    def save(self):
        user = self.context.get('request').user
        user.transaction_pin = make_password(self.validated_data['pin'])
        user.pin_set = True
        user.save(update_fields=['transaction_pin', 'pin_set'])
        return user


class VerifyPinSerializer(serializers.Serializer):
    """Serializer for verifying a transaction PIN before sending money."""
    pin = serializers.CharField(
        max_length=4,
        min_length=4,
        write_only=True,
        help_text="4-digit transaction PIN"
    )

    def validate_pin(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('PIN must contain only digits.')
        return value

    def validate(self, attrs):
        user = self.context.get('request').user
        if not user.pin_set or not user.transaction_pin:
            raise serializers.ValidationError('Transaction PIN not set. Please set your PIN first.')
        if not check_password(attrs['pin'], user.transaction_pin):
            raise serializers.ValidationError({'pin': 'Incorrect PIN. Please try again.'})
        return attrs


class UserMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal user serializer for nested representations.
    """

    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'full_name', 'is_verified']
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Creates user and auto-creates wallet via signal.
    """

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password_strength],
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'phone', 'password', 'confirm_password',
            'first_name', 'last_name', 'date_of_birth', 'address', 'city', 'country'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'phone': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate_phone(self, value):
        validate_phone(value)
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match.'
            })
        return attrs

    def create(self, validated_data):
        # Remove confirm_password before creating user
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """

    old_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password_strength],
        style={'input_type': 'password'}
    )
    confirm_new_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )

    def validate_old_password(self, value):
        user = self.context.get('request').user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({
                'confirm_new_password': 'New passwords do not match.'
            })
        return attrs

    def save(self):
        user = self.context.get('request').user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for forgot password functionality.
    Generates a password reset token.
    """

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        try:
            self.user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'No account found with this email address.'
            )
        return value

    def save(self):
        user = self.user
        # Generate a temporary reset token (in production, use Django's built-in token system)
        reset_token = str(uuid.uuid4())

        # Store token temporarily (in production, use a proper token model or cache)
        # For now, we'll just send an email notification
        if settings.DEBUG:
            # In development, just log the token
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Password reset token for {user.email}: {reset_token}")

        # In production, send actual email
        try:
            send_mail(
                subject='Password Reset Request - Digital Wallet',
                message=f'Your password reset token is: {reset_token}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass

        return reset_token


class UpdateProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile information.
    """

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone',
            'date_of_birth', 'address', 'city', 'country',
            'profile_picture'
        ]
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'phone': {'required': False},
        }

    def validate_phone(self, value):
        validate_phone(value)
        # Check uniqueness if phone is being changed
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(phone=value).exists():
            raise serializers.ValidationError('A user with this phone number already exists.')
        return value


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that includes user data in the response.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['role'] = user.role
        token['is_verified'] = user.is_verified
        token['phone'] = user.phone
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add user data to the response
        data.update({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user': {
                    'id': self.user.id,
                    'username': self.user.username,
                    'email': self.user.email,
                    'phone': self.user.phone,
                    'first_name': self.user.first_name,
                    'last_name': self.user.last_name,
                    'full_name': self.user.full_name,
                    'role': self.user.role,
                    'is_verified': self.user.is_verified,
                    'profile_picture': self.user.profile_picture.url if self.user.profile_picture else None,
                    'wallet_number': self.user.wallet_id.wallet_number if self.user.wallet_id else None,
                    'balance': str(self.user.wallet_id.balance) if self.user.wallet_id else '0.00',
                },
                'tokens': {
                    'access': data.get('access'),
                    'refresh': data.get('refresh'),
                }
            }
        })

        # Remove the flat token keys since they're nested in data
        if 'access' in data:
            del data['access']
        if 'refresh' in data:
            del data['refresh']

        return data


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer for the AuditLog model.
    """

    username = serializers.CharField(source='user.username', read_only=True, default='Anonymous')

    class Meta:
        model = User._meta.get_field('audit_logs').related_model
        fields = [
            'id', 'user', 'username', 'action', 'model_name',
            'object_id', 'changes', 'ip_address', 'created_at'
        ]
        read_only_fields = fields
