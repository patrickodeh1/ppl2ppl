from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import FormView, TemplateView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError

import secrets
import string
import logging
from datetime import timedelta

from .models import CustomUser, EmailVerificationToken, PasswordResetToken, LoginSession
from .forms import (
    UserRegistrationForm, UserLoginForm, ForgotPasswordForm,
    ResetPasswordForm
)
from .utils import send_email_verification, send_password_reset_email

logger = logging.getLogger(__name__)


class RegisterView(FormView):
    """Handle user registration."""
    
    template_name = 'authentication/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('authentication:email-verification')
    
    def form_valid(self, form):
        """Process valid registration form."""
        with transaction.atomic():
            # Create user
            user = form.save(commit=False)
            user.status = 'registered'
            user.save()
            logger.info(f"[USER_REGISTERED] Status: Created")
            
            # Generate and save email verification token
            logger.info(f"[VERIFY_EMAIL] Generating token for user {user.id}")
            token = self._generate_token()
            EmailVerificationToken.objects.create(
                user=user,
                token=token
            )
            logger.info(f"[VERIFY_EMAIL] Token created: {token[:8]}...")
            
            # Send verification email
            logger.info(f"[VERIFY_EMAIL] Attempting to send verification email")
            try:
                send_email_verification(self.request, user, token)
                logger.info(f"[VERIFY_EMAIL] Email sending completed successfully")
            except Exception as e:
                import traceback
                logger.error(f"[EMAIL_FAILED] Verification - Error: {type(e).__name__}: {str(e)}")
                logger.error(f"[EMAIL_FAILED] Traceback: {traceback.format_exc()}")
            
            # Store user id in session for verification page
            self.request.session['verification_user_id'] = user.id
            self.request.session['verification_email'] = user.email
            logger.info(f"[VERIFY_EMAIL] Session data stored for user {user.id}")
        
        messages.success(self.request, 'Registration successful! Please check your email to verify your account.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle invalid form submission."""
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)
    
    @staticmethod
    def _generate_token():
        """Generate a secure random token."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for i in range(32))


class EmailVerificationView(TemplateView):
    """Display email verification page."""
    
    template_name = 'authentication/email-verification.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.request.session.get('verification_email', '')
        context['email'] = email
        return context


class VerifyEmailView(View):
    """Handle email verification with token."""
    
    def get(self, request, token):
        """Verify email with provided token."""
        try:
            verification_token = EmailVerificationToken.objects.get(token=token)
            
            if not verification_token.is_valid():
                messages.error(request, 'Verification link has expired. Please request a new one.')
                return redirect('authentication:register')
            
            # Mark token as used
            verification_token.is_used = True
            verification_token.used_at = timezone.now()
            verification_token.save()
            
            # Update user status
            user = verification_token.user
            user.is_email_verified = True
            user.status = 'email_verified'
            user.save()
            logger.info(f"[EMAIL_VERIFIED] Status: Success")
            
            # Clear session
            if 'verification_user_id' in request.session:
                del request.session['verification_user_id']
            if 'verification_email' in request.session:
                del request.session['verification_email']
            
            messages.success(request, 'Email verified successfully! You can now log in.')
            return redirect('authentication:login')
        
        except EmailVerificationToken.DoesNotExist:
            logger.warning(f"[EMAIL_VERIFY] Invalid token - Status: Failed")
            messages.error(request, 'Invalid verification link.')
            return redirect('authentication:register')


class LoginView(FormView):
    """Handle user login."""
    
    template_name = 'authentication/login.html'
    form_class = UserLoginForm
    success_url = reverse_lazy('core:training-dashboard')  # Redirect to training dashboard
    
    def form_valid(self, form):
        """Process valid login form."""
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        remember_me = form.cleaned_data.get('remember_me')
        
        user = CustomUser.objects.get(email=email)
        
        # Check if email is verified
        if not user.is_email_verified:
            logger.warning(f"[LOGIN_FAILED] Email unverified - Status: Blocked")
            messages.error(
                self.request,
                'Please verify your email address before logging in. Check your inbox for the verification email.'
            )
            self.request.session['unverified_email'] = email
            return redirect('authentication:email-verification')
        
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


class ForgotPasswordView(FormView):
    """Handle forgot password requests."""
    
    template_name = 'authentication/forgot-password.html'
    form_class = ForgotPasswordForm
    success_url = reverse_lazy('authentication:reset-password-sent')
    
    def form_valid(self, form):
        """Process valid forgot password form."""
        email = form.cleaned_data.get('email')
        
        try:
            user = CustomUser.objects.get(email=email)
            
            # Invalidate any existing password reset tokens
            PasswordResetToken.objects.filter(user=user).delete()
            
            # Generate new password reset token
            token = self._generate_token()
            PasswordResetToken.objects.create(
                user=user,
                token=token
            )
            
            # Send reset email
            try:
                send_password_reset_email(self.request, user, token)
                logger.info(f"[PASSWORD_RESET] Email sent - Status: Success")
            except Exception as e:
                import traceback
                logger.error(f"[EMAIL_FAILED] Password reset - Error: {type(e).__name__}: {str(e)}")
                logger.error(f"[EMAIL_FAILED] Traceback: {traceback.format_exc()}")
            
            # Store email in session for confirmation page
            self.request.session['reset_password_email'] = email
        
        except CustomUser.DoesNotExist:
            logger.warning(f"[PASSWORD_RESET] Email not found - Status: Not found")
            # Don't reveal if email exists in system
            pass
        
        return super().form_valid(form)
    
    @staticmethod
    def _generate_token():
        """Generate a secure random token."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for i in range(32))


class ResetPasswordSentView(TemplateView):
    """Confirmation page after reset email is sent."""
    
    template_name = 'authentication/reset-password-sent.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.request.session.get('reset_password_email', '')
        context['email'] = email
        return context


class ResetPasswordView(FormView):
    """Handle password reset with token."""
    
    template_name = 'authentication/reset-password.html'
    form_class = ResetPasswordForm
    success_url = reverse_lazy('authentication:reset-password-success')
    
    def dispatch(self, request, token, *args, **kwargs):
        """Verify token before processing."""
        try:
            self.reset_token = PasswordResetToken.objects.get(token=token)
            
            if not self.reset_token.is_valid():
                messages.error(request, 'Password reset link has expired. Please request a new one.')
                return redirect('authentication:forgot-password')
        
        except PasswordResetToken.DoesNotExist:
            messages.error(request, 'Invalid password reset link.')
            return redirect('authentication:forgot-password')
        
        return super().dispatch(request, token, *args, **kwargs)
    
    def form_valid(self, form):
        """Process valid password reset form."""
        new_password = form.cleaned_data.get('new_password')
        
        user = self.reset_token.user
        user.set_password(new_password)
        user.save()
        
        # Mark token as used
        self.reset_token.is_used = True
        self.reset_token.used_at = timezone.now()
        self.reset_token.save()
        
        messages.success(self.request, 'Password reset successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email'] = self.reset_token.user.email
        return context


class ResetPasswordSuccessView(TemplateView):
    """Confirmation page after successful password reset."""
    
    template_name = 'authentication/reset-password-success.html'


class ResendVerificationEmailView(View):
    """Handle resending verification email."""
    
    def post(self, request):
        """Resend verification email."""
        email = request.POST.get('email')
        
        try:
            user = CustomUser.objects.get(email=email, is_email_verified=False)
            
            # Delete old token if exists
            EmailVerificationToken.objects.filter(user=user).delete()
            
            # Generate new token
            token = self._generate_token()
            EmailVerificationToken.objects.create(
                user=user,
                token=token
            )
            
            # Send verification email
            send_email_verification(request, user, token)
            
            messages.success(request, 'Verification email sent! Please check your inbox.')
        
        except CustomUser.DoesNotExist:
            messages.error(request, 'Invalid email address.')
        
        return redirect('authentication:email-verification')
    
    @staticmethod
    def _generate_token():
        """Generate a secure random token."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for i in range(32))


class UserProfileView(LoginRequiredMixin, TemplateView):
    """Display user profile."""
    
    template_name = 'authentication/profile.html'
    login_url = reverse_lazy('authentication:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
