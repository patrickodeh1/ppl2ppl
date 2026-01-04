from django.shortcuts import redirect
from django.views import View
from django.views.generic import FormView, TemplateView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.db import transaction

import secrets
import logging
from datetime import timedelta

from .models import CustomUser, LoginSession
from .forms import UserRegistrationForm, UserLoginForm

logger = logging.getLogger(__name__)


class RegisterView(FormView):
    """Handle user registration."""
    
    template_name = 'authentication/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('authentication:login')
    
    def post(self, request, *args, **kwargs):
        """Log POST request received."""
        logger.info(f"[USER_REGISTERED] POST request received - Starting registration")
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Process valid registration form."""
        with transaction.atomic():
            # Create user
            user = form.save(commit=False)
            user.save()
            logger.info(f"[USER_REGISTERED] Status: Created")
        
        messages.success(self.request, 'Registration successful! You can now log in.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle invalid form submission."""
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)


class LoginView(FormView):
    """Handle user login."""
    
    template_name = 'authentication/login.html'
    form_class = UserLoginForm
    success_url = reverse_lazy('core:training-dashboard')  # Default redirect
    
    def form_valid(self, form):
        """Process valid login form."""
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        remember_me = form.cleaned_data.get('remember_me')
        
        user = CustomUser.objects.get(email=email)
        
        # Reset failed login attempts on successful login
        user.reset_login_attempts()
        
        # Authenticate and login
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
            logger.info(f"[USER_LOGIN] Status: Success")
            
            # Create login session
            self._create_login_session(user, remember_me)
            
            # Set session timeout
            if not remember_me:
                self.request.session.set_expiry(timedelta(hours=2))
            else:
                self.request.session.set_expiry(timedelta(days=30))
            
            messages.success(self.request, f'Welcome back, {user.first_name}!')
            
            # Redirect certified users to schedule, others to training dashboard
            try:
                if user.certification and user.certification.is_certified:
                    self.success_url = reverse_lazy('core:office-schedule')
                else:
                    self.success_url = reverse_lazy('core:training-dashboard')
            except:
                # No certification exists, use training dashboard
                self.success_url = reverse_lazy('core:training-dashboard')
            
            return super().form_valid(form)
        
        messages.error(self.request, 'Login failed. Please try again.')
        return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Handle invalid form submission."""
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    messages.error(self.request, error)
                else:
                    messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)
    
    @staticmethod
    def _create_login_session(user, remember_me):
        """Create a login session record."""
        # This would normally use request metadata
        session_key = secrets.token_urlsafe(32)
        LoginSession.objects.create(
            user=user,
            session_key=session_key,
            ip_address='127.0.0.1',  # Would be extracted from request in production
            user_agent='',  # Would be extracted from request in production
            remember_me=remember_me
        )


class LogoutView(LoginRequiredMixin, View):
    """Handle user logout."""
    
    def post(self, request):
        """Log out the user."""
        user = request.user
        
        # Deactivate all sessions
        LoginSession.objects.filter(user=user).update(is_active=False)
        
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('authentication:login')


class PasswordResetRequestView(TemplateView):
    """Display password reset request page directing users to contact admin."""
    
    template_name = 'authentication/password-reset-request.html'


class UserProfileView(LoginRequiredMixin, TemplateView):
    """Display user profile."""
    
    template_name = 'authentication/profile.html'
    login_url = reverse_lazy('authentication:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
