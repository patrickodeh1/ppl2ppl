from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Registration & Login
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Password Reset (admin-only)
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password-reset'),
    
    # User Profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
]
