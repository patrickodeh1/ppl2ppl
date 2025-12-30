from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Registration
    path('register/', views.RegisterView.as_view(), name='register'),
    path('email-verification/', views.EmailVerificationView.as_view(), name='email-verification'),
    path('verify-email/<str:token>/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', views.ResendVerificationEmailView.as_view(), name='resend-verification'),
    
    # Login & Logout
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Password Management
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password-sent/', views.ResetPasswordSentView.as_view(), name='reset-password-sent'),
    path('reset-password/<str:token>/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('reset-password-success/', views.ResetPasswordSuccessView.as_view(), name='reset-password-success'),
    
    # User Profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
]
