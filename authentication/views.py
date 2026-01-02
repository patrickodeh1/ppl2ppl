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
from datetime import timedelta

from .models import CustomUser, EmailVerificationToken, PasswordResetToken, LoginSession
from .forms import (
    UserRegistrationForm, UserLoginForm, ForgotPasswordForm,
    ResetPasswordForm
)


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
            
            # Generate and save email verification token
            token = self._generate_token()
            EmailVerificationToken.objects.create(
                user=user,
                token=token
            )
            
            # Send verification email
            self._send_verification_email(user, token)
            
            # Store user id in session for verification page
            self.request.session['verification_user_id'] = user.id
            self.request.session['verification_email'] = user.email
        
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
    
    @staticmethod
    def _send_verification_email(user, token):
        """Send email verification link to user."""
        # In production, use reverse() with request to get full URL
        verification_link = f"https://yourdomain.com/auth/verify-email/{token}/"
        
        subject = 'Verify Your Email Address'
        message = f"""
        Hello {user.first_name},
        
        Thank you for registering with us. Please verify your email address by clicking the link below:
        
        {verification_link}
        
        This link will expire in 24 hours.
        
        If you did not create this account, please ignore this email.
        
        Best regards,
        The Team
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            # Log the error but don't fail registration
            print(f"Failed to send verification email: {e}")
            # In production, you might want to log this properly
            pass


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
            
            # Clear session
            if 'verification_user_id' in request.session:
                del request.session['verification_user_id']
            if 'verification_email' in request.session:
                del request.session['verification_email']
            
            messages.success(request, 'Email verified successfully! You can now log in.')
            return redirect('authentication:login')
        
        except EmailVerificationToken.DoesNotExist:
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
            self._send_reset_email(user, token)
            
            # Store email in session for confirmation page
            self.request.session['reset_password_email'] = email
        
        except CustomUser.DoesNotExist:
            # Don't reveal if email exists in system
            pass
        
        return super().form_valid(form)
    
    @staticmethod
    def _generate_token():
        """Generate a secure random token."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for i in range(32))
    
    @staticmethod
    def _send_reset_email(user, token):
        """Send password reset link to user."""
        reset_link = f"https://yourdomain.com/auth/reset-password/{token}/"
        
        subject = 'Reset Your Password'
        message = f"""
        Hello {user.first_name},
        
        You requested to reset your password. Please click the link below to reset it:
        
        {reset_link}
        
        This link will expire in 1 hour.
        
        If you did not request a password reset, please ignore this email.
        
        Best regards,
        The Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


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
            RegisterView._send_verification_email(user, token)
            
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
