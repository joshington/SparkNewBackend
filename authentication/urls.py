
from django.urls import path
from .views import*

app_name = 'authentication'


urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('validate-otp/', ValidateOTPView.as_view()),
    path('create-pin/', CreatePinView.as_view()),
    path('create-new-pin/',CreatePinView.as_view()),
    path('login-user/',LoginView.as_view()),
    path('create-username/',AddUsernameView.as_view()),
    path('register-admin/',RegisterAdmin.as_view()),
    path('login-admin/',AdminLoginView.as_view()),
    path('user-analytics/',UserAnalyticsView.as_view()),
]
