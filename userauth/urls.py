# userauth/urls.py
from django.urls import path
from .views import (
    RegisterView, LogoutView, PasswordResetRequestView, PasswordResetConfirmView,
    ProtectedView, AccountActivationView,CustomLoginView,AddCustomerView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'), 
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('activate/<uidb64>/<token>/', AccountActivationView.as_view(), name='account_activation'),
    path('profile/', ProtectedView.as_view(), name='profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('add-customer/', AddCustomerView.as_view(), name='add_customer'),
]
