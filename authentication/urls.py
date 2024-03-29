
from django.urls import path
from .views import*

app_name = 'authentication'


urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('validate-otp/', ValidateOTPView.as_view()),
    path('resend-otp/', ResendOTPView.as_view()),
    path('create-pin/', CreatePinView.as_view()),
    path('create-new-pin/',ForgotPINView.as_view()),
    path('login-user/',LoginView.as_view()),
    path('update-user/<pk>/',UpdateUserAPIView.as_view()),
    path('update-admin/<pk>/',UpdateAdminAPIView.as_view()),
    path('create-username/',AddUsernameView.as_view()),
    path('register-admin/',RegisterAdmin.as_view()),
    path('login-admin/',AdminLoginView.as_view()),
    path('user-analytics/',UserAnalyticsView.as_view()),
    path('get_admin_details/',AdminDetails.as_view()),
]
