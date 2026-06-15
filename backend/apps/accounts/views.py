from django.db import models as db_models
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from django.contrib.auth import get_user_model

from .serializers import (
    RegisterSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    UpdateProfileSerializer,
    CustomTokenObtainPairSerializer,
    SetPinSerializer,
    VerifyPinSerializer,
)
from .permissions import IsOwnerOrAdmin, IsAdmin

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Register a new user. Auto-creates a wallet with $1000 balance via signal.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Refresh user to get wallet relation (created by signal)
        user.refresh_from_db()

        # Return user data with wallet info
        user_serializer = UserSerializer(user)

        return Response({
            'success': True,
            'message': 'Registration successful. Wallet created with $1,000.00 balance.',
            'data': {
                'user': user_serializer.data,
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    POST /api/auth/login/
    Login with username/email and password. Returns JWT access + refresh tokens.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({
                'success': False,
                'message': 'Invalid credentials.',
                'data': None,
            }, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    GET /api/auth/profile/ - Retrieve current user's profile
    PUT /api/auth/profile/ - Update current user's profile
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return UpdateProfileSerializer
        return UserSerializer

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response({
            'success': True,
            'message': 'Profile retrieved successfully',
            'data': serializer.data,
        })

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return full user data after update
        user.refresh_from_db()
        response_serializer = UserSerializer(user)

        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'data': response_serializer.data,
        })


class ChangePasswordView(APIView):
    """
    PUT /api/auth/change-password/
    Change the authenticated user's password.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'success': True,
            'message': 'Password changed successfully',
            'data': None,
        })


class ForgotPasswordView(APIView):
    """
    POST /api/auth/forgot-password/
    Request a password reset token sent to email.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reset_token = serializer.save()

        return Response({
            'success': True,
            'message': 'Password reset instructions have been sent to your email.',
            'data': {
                'reset_token': reset_token if reset_token else None,
            }
        })


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Logout the user by blacklisting the refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = OutstandingToken.objects.get(token=refresh_token)
                BlacklistedToken.objects.create(token=token)

            return Response({
                'success': True,
                'message': 'Logged out successfully',
                'data': None,
            })
        except OutstandingToken.DoesNotExist:
            return Response({
                'success': True,
                'message': 'Logged out successfully',
                'data': None,
            })
        except Exception:
            return Response({
                'success': True,
                'message': 'Logged out successfully',
                'data': None,
            })


class AdminUserListView(generics.ListAPIView):
    """
    GET /api/auth/admin/users/
    Admin-only endpoint to list all users.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_joined')

        # Filter by role
        role = self.request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(role=role)

        # Filter by verification status
        is_verified = self.request.query_params.get('is_verified', None)
        if is_verified is not None:
            is_verified_bool = is_verified.lower() in ('true', '1', 'yes')
            queryset = queryset.filter(is_verified=is_verified_bool)

        # Search by username, email, or phone
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                db_models.Q(username__icontains=search) |
                db_models.Q(email__icontains=search) |
                db_models.Q(phone__icontains=search)
            )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Users retrieved successfully',
            'data': serializer.data,
        })


class SetPinView(APIView):
    """
    POST /api/auth/set-pin/
    Set or change the 4-digit transaction PIN.
    Required before sending money.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SetPinSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'success': True,
            'message': 'Transaction PIN set successfully',
            'data': None,
        })


class VerifyPinView(APIView):
    """
    POST /api/auth/verify-pin/
    Verify the 4-digit transaction PIN before sending money.
    Returns a verification token valid for 5 minutes.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VerifyPinSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        # Generate a short-lived verification token
        import uuid
        from django.core.cache import cache

        verification_token = str(uuid.uuid4())
        cache_key = f'pin_verified_{request.user.id}'
        cache.set(cache_key, verification_token, timeout=300)  # 5 minutes

        return Response({
            'success': True,
            'message': 'PIN verified successfully',
            'data': {
                'verification_token': verification_token,
            }
        })
