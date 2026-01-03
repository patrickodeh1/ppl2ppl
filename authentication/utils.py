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
    try:
        logger.info(f"[VERIFY_EMAIL] Starting verification email for user: {user.email}")
        
        # Build verification link
        logger.info(f"[VERIFY_EMAIL] Building verification link with token: {token[:8]}...")
        verification_link = request.build_absolute_uri(
            reverse('authentication:verify-email', kwargs={'token': token})
        )
        logger.info(f"[VERIFY_EMAIL] Built verification link successfully")
        
        context = {
            'user': user,
            'verification_link': verification_link,
            'expiration_hours': 24,
        }
        
        # Email subject and message
        logger.info(f"[VERIFY_EMAIL] Rendering email template")
        subject = 'Verify Your Email Address'
        html_message = render_to_string(
            'emails/email_verification.html',
            context
        )
        logger.info(f"[VERIFY_EMAIL] Template rendered successfully ({len(html_message)} bytes)")
        plain_message = strip_tags(html_message)
        
        logger.info(f"[VERIFY_EMAIL] Sending email via SMTP to {user.email}")
        result = send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"[EMAIL_SENT] Verification email - Status: Success - Result: {result}")
        return result
    except TimeoutError as e:
        logger.error(f"[EMAIL_FAILED] Verification email - Error: SMTP Timeout - Check EMAIL_HOST setting")
        import traceback
        logger.error(f"[EMAIL_FAILED] Traceback: {traceback.format_exc()}")
        raise
    except Exception as e:
        logger.error(f"[EMAIL_FAILED] Verification email - Error: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"[EMAIL_FAILED] Traceback: {traceback.format_exc()}")
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
    try:
        logger.info(f"[PASSWORD_RESET] Starting password reset email for user: {user.email}")
        
        # Build reset link
        logger.info(f"[PASSWORD_RESET] Building reset link with token: {token[:8]}...")
        reset_link = request.build_absolute_uri(
            reverse('authentication:reset-password', kwargs={'token': token})
        )
        logger.info(f"[PASSWORD_RESET] Built reset link successfully")
        
        context = {
            'user': user,
            'reset_link': reset_link,
            'expiration_hours': 1,
        }
        
        # Email subject and message
        logger.info(f"[PASSWORD_RESET] Rendering email template")
        subject = 'Reset Your Password'
        html_message = render_to_string(
            'emails/password_reset.html',
            context
        )
        logger.info(f"[PASSWORD_RESET] Template rendered successfully ({len(html_message)} bytes)")
        plain_message = strip_tags(html_message)
        
        logger.info(f"[PASSWORD_RESET] Sending email via SMTP to {user.email}")
        result = send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"[EMAIL_SENT] Password reset email - Status: Success - Result: {result}")
        return result
    except TimeoutError as e:
        logger.error(f"[EMAIL_FAILED] Password reset email - Error: SMTP Timeout - Check EMAIL_HOST setting")
        import traceback
        logger.error(f"[EMAIL_FAILED] Traceback: {traceback.format_exc()}")
        raise
    except Exception as e:
        logger.error(f"[EMAIL_FAILED] Password reset email - Error: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"[EMAIL_FAILED] Traceback: {traceback.format_exc()}")
        raise
    except Exception as e:
        logger.error(f"[EMAIL_FAILED] Password reset email - Error: {type(e).__name__}: {str(e)}")
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
