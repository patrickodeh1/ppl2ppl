from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication'
    
    def ready(self):
        import authentication.signals
        from django.conf import settings
        
        # Log email configuration on startup
        logger.info(f"Authentication app initialized")
        logger.info(f"Email Backend: {settings.EMAIL_BACKEND}")
        logger.info(f"Email Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        logger.info(f"Email Host User: {settings.EMAIL_HOST_USER}")
        logger.info(f"Default From Email: {settings.DEFAULT_FROM_EMAIL}")
        logger.info(f"Email Use SSL: {settings.EMAIL_USE_SSL}")
        logger.info(f"Email Use TLS: {settings.EMAIL_USE_TLS}")
