from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator, FileExtensionValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
import re


class CustomUserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create a regular user with email and password."""
        if not email:
            raise ValueError('Email address is required')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create a superuser with email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_email_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Custom user model with email-based authentication."""
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, db_index=True)
    
    # Contact Information
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message='Phone number must be valid. Include country code if needed (e.g., +1234567890)'
    )
    phone_number = models.CharField(
        max_length=20,
        validators=[phone_regex],
        help_text='Phone number with country code (e.g., +12025551234)'
    )
    
    # Address Information
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state_region = models.CharField(max_length=100)
    zip_postal_code = models.CharField(max_length=20, blank=True)
    
    # Profile Information
    date_of_birth = models.DateField()
    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])]
    )
    
    # Account Status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_certified = models.BooleanField(default=False)
    
    # Registration & Authentication
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    terms_accepted = models.BooleanField(default=False)
    terms_accepted_at = models.DateTimeField(null=True, blank=True)
    
    # Account Security
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Registration Status
    STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('email_verified', 'Email Verified'),
        ('active', 'Active'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number', 'date_of_birth', 'city', 'state_region']
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_email_verified']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def clean(self):
        """Validate user data."""
        super().clean()
        
        # Validate date of birth (must be 18+)
        from datetime import date
        today = date.today()
        age = today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
        if age < 18:
            raise ValidationError({'date_of_birth': 'You must be at least 18 years old to register.'})
    
    def is_account_locked(self):
        """Check if account is locked due to failed login attempts."""
        if self.account_locked_until and timezone.now() < self.account_locked_until:
            return True
        elif self.account_locked_until and timezone.now() >= self.account_locked_until:
            # Unlock the account if lock period has expired
            self.account_locked_until = None
            self.failed_login_attempts = 0
            self.save()
            return False
        return False
    
    def record_failed_login(self):
        """Record a failed login attempt and lock account if necessary."""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            # Lock account for 30 minutes after 5 failed attempts
            self.account_locked_until = timezone.now() + timedelta(minutes=30)
        self.save()
    
    def reset_login_attempts(self):
        """Reset failed login attempts and unlock account."""
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.last_login = timezone.now()
        self.save()


class EmailVerificationToken(models.Model):
    """Store email verification tokens."""
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='email_verification_token')
    token = models.CharField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    
    def is_valid(self):
        """Check if token is still valid (24 hours)."""
        if self.is_used:
            return False
        return timezone.now() - self.created_at <= timedelta(hours=24)
    
    def __str__(self):
        return f"Email verification token for {self.user.email}"


class PasswordResetToken(models.Model):
    """Store password reset tokens."""
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='password_reset_token')
    token = models.CharField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    
    def is_valid(self):
        """Check if token is still valid (1 hour)."""
        if self.is_used:
            return False
        return timezone.now() - self.created_at <= timedelta(hours=1)
    
    def __str__(self):
        return f"Password reset token for {self.user.email}"


class LoginSession(models.Model):
    """Track user login sessions for "Remember Me" functionality."""
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='login_sessions')
    session_key = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    remember_me = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    SESSION_TIMEOUT_HOURS = 2
    
    def is_session_valid(self):
        """Check if session is still valid (2 hour timeout)."""
        if not self.is_active:
            return False
        timeout = timezone.now() - timedelta(hours=self.SESSION_TIMEOUT_HOURS)
        return self.last_activity > timeout
    
    class Meta:
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"Session for {self.user.email} - {self.created_at}"
