from django.urls import path, include

from . import views
from .views import OTPVerificationView

urlpatterns = [
    path("signup/", views.SignupAPIView.as_view(), name="user-signup"),

    path("login/", views.LoginAPIView.as_view(), name="user-login"),
    path('verify_otp/', OTPVerificationView.as_view(), name='verify_otp'),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),

  ]