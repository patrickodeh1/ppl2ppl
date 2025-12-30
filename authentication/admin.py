from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, EmailVerificationToken, PasswordResetToken, LoginSession


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Custom admin for CustomUser model."""
    
    list_display = ('email', 'full_name', 'is_active', 'is_email_verified', 'is_certified', 'status', 'created_at')
    list_filter = ('is_active', 'is_email_verified', 'is_certified', 'status', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    
    fieldsets = (
        ('Email & Password', {
            'fields': ('email', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'profile_photo')
        }),
        ('Contact Information', {
            'fields': ('phone_number',)
        }),
        ('Address Information', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state_region', 'zip_postal_code')
        }),
        ('Account Status', {
            'fields': ('is_active', 'status', 'is_email_verified', 'is_certified', 'is_staff', 'is_superuser')
        }),
        ('Registration & Terms', {
            'fields': ('terms_accepted', 'terms_accepted_at')
        }),
        ('Security', {
            'fields': ('failed_login_attempts', 'account_locked_until'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_login'),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'phone_number', 'date_of_birth', 'city', 'state_region')
        }),
    )


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """Admin for EmailVerificationToken model."""
    
    list_display = ('user', 'is_valid', 'is_used', 'created_at', 'used_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__email', 'token')
    readonly_fields = ('token', 'created_at', 'used_at')
    
    fieldsets = (
        ('Token Information', {
            'fields': ('user', 'token')
        }),
        ('Status', {
            'fields': ('is_used',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'used_at')
        }),
    )


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """Admin for PasswordResetToken model."""
    
    list_display = ('user', 'is_valid', 'is_used', 'created_at', 'used_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__email', 'token')
    readonly_fields = ('token', 'created_at', 'used_at')
    
    fieldsets = (
        ('Token Information', {
            'fields': ('user', 'token')
        }),
        ('Status', {
            'fields': ('is_used',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'used_at')
        }),
    )


@admin.register(LoginSession)
class LoginSessionAdmin(admin.ModelAdmin):
    """Admin for LoginSession model."""
    
    list_display = ('user', 'remember_me', 'is_active', 'created_at', 'last_activity')
    list_filter = ('remember_me', 'is_active', 'created_at')
    search_fields = ('user__email', 'ip_address')
    readonly_fields = ('created_at', 'last_activity', 'session_key')
    
    fieldsets = (
        ('Session Information', {
            'fields': ('user', 'session_key', 'remember_me')
        }),
        ('Network Information', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_activity')
        }),
    )
