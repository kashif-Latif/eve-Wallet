from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    LoginView,
    ProfileView,
    ChangePasswordView,
    ForgotPasswordView,
    LogoutView,
    AdminUserListView,
    SetPinView,
    VerifyPinView,
)

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),

    # Transaction PIN
    path('set-pin/', SetPinView.as_view(), name='set_pin'),
    path('verify-pin/', VerifyPinView.as_view(), name='verify_pin'),

    # Admin
    path('admin/users/', AdminUserListView.as_view(), name='admin_users'),
]
