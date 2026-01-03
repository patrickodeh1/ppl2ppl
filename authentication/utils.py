"""Utility functions for authentication app."""

from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


def send_email_verification(request, user, token):
    """
    Send email verification link to user.
    
    Args:
        request: HTTP request object
        user: CustomUser instance
        token: Email verification token
        
    Raises:
        Exception: If email sending fails
    """
    # Build verification link
    verification_link = request.build_absolute_uri(
        reverse('authentication:verify-email', kwargs={'token': token})
    )
    
    logger.debug(f"Building verification link for {user.email}: {verification_link}")
    
    context = {
        'user': user,
        'verification_link': verification_link,
        'expiration_hours': 24,
    }
    
    # Email subject and message
    subject = 'Verify Your Email Address'
    html_message = render_to_string(
        'authentication/emails/email_verification.html',
        context
    )
    plain_message = strip_tags(html_message)
    
    logger.debug(f"Sending verification email to {user.email} from {settings.DEFAULT_FROM_EMAIL}")
    
    try:
        result = send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Verification email sent successfully to {user.email} (result: {result})")
        return result
    except Exception as e:
        logger.error(f"FAILED to send verification email to {user.email}: {type(e).__name__}: {str(e)}")
        raise


def send_password_reset_email(request, user, token):
    """
    Send password reset link to user.
    
    Args:
        request: HTTP request object
        user: CustomUser instance
        token: Password reset token
        
    Raises:
        Exception: If email sending fails
    """
    # Build reset link
    reset_link = request.build_absolute_uri(
        reverse('authentication:reset-password', kwargs={'token': token})
    )
    
    logger.debug(f"Building reset link for {user.email}: {reset_link}")
    
    context = {
        'user': user,
        'reset_link': reset_link,
        'expiration_hours': 1,
    }
    
    # Email subject and message
    subject = 'Reset Your Password'
    html_message = render_to_string(
        'authentication/emails/password_reset.html',
        context
    )
    plain_message = strip_tags(html_message)
    
    logger.debug(f"Sending password reset email to {user.email} from {settings.DEFAULT_FROM_EMAIL}")
    
    try:
        result = send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Password reset email sent successfully to {user.email} (result: {result})")
        return result
    except Exception as e:
        logger.error(f"FAILED to send password reset email to {user.email}: {type(e).__name__}: {str(e)}")
        raise


def get_password_strength_class(password):
    """
    Get CSS class for password strength indicator.
    
    Args:
        password: Password string
        
    Returns:
        Tuple of (strength_level, css_class, description)
    """
    import re
    
    score = 0
    
    # Length scoring
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1
    
    # Character variety scoring
    if re.search(r'[a-z]', password):
        score += 1
    if re.search(r'[A-Z]', password):
        score += 1
    if re.search(r'[0-9]', password):
        score += 1
    if re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
        score += 1
    
    if score <= 2:
        return ('weak', 'danger', 'Weak')
    elif score <= 4:
        return ('medium', 'warning', 'Medium')
    else:
        return ('strong', 'success', 'Strong')
