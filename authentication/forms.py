from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import re

from .models import CustomUser, EmailVerificationToken, PasswordResetToken


# ============================================================================
# PASSWORD STRENGTH WIDGET
# ============================================================================

class PasswordStrengthWidget(forms.PasswordInput):
    """Custom password widget with strength indicator"""
    
    template_name = 'widgets/password_strength_widget.html'
    
    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.attrs['class'] = 'form-control password-strength-input'
        self.attrs['data-password-strength'] = 'true'
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        return context


# ============================================================================
# PASSWORD STRENGTH MIXIN
# ============================================================================

class PasswordStrengthMixin:
    """Mixin to validate password strength requirements."""
    
    PASSWORD_MIN_LENGTH = 8
    
    def validate_password_strength(self, password):
        """
        Validate password meets requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        """
        errors = []
        
        if len(password) < self.PASSWORD_MIN_LENGTH:
            errors.append(f'Password must be at least {self.PASSWORD_MIN_LENGTH} characters long.')
        
        if not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter.')
        
        if not re.search(r'[a-z]', password):
            errors.append('Password must contain at least one lowercase letter.')
        
        if not re.search(r'[0-9]', password):
            errors.append('Password must contain at least one number.')
        
        return errors
    
    def get_password_strength(self, password):
        """Return password strength: 'weak', 'medium', or 'strong'."""
        score = 0
        
        # Length score
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        
        # Character variety score
        if re.search(r'[a-z]', password):
            score += 1
        if re.search(r'[A-Z]', password):
            score += 1
        if re.search(r'[0-9]', password):
            score += 1
        if re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
            score += 1
        
        if score <= 3:
            return 'weak'
        elif score <= 5:
            return 'medium'
        else:
            return 'strong'


class UserRegistrationForm(forms.ModelForm, PasswordStrengthMixin):
    """Form for user registration."""
    
    password = forms.CharField(
        widget=PasswordStrengthWidget(attrs={
            'placeholder': 'Password (min 8 chars, uppercase, lowercase, number)',
        }),
        help_text='Minimum 8 characters, must include uppercase, lowercase, and number'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
        })
    )
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='I accept the Terms & Conditions'
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'date_of_birth', 'city', 'state_region',
            'address_line_1', 'address_line_2', 'zip_postal_code',
            'profile_photo'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number (with country code, e.g., +12025551234)'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state_region': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State/Region'
            }),
            'address_line_1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Address Line 1 (Optional)'
            }),
            'address_line_2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Address Line 2 (Optional)'
            }),
            'zip_postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Zip/Postal Code (Optional)'
            }),
            'profile_photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name or len(first_name.strip()) == 0:
            raise ValidationError('First name is required.')
        return first_name.strip()
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name or len(last_name.strip()) == 0:
            raise ValidationError('Last name is required.')
        return last_name.strip()
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('This email address is already registered.')
        return email
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number:
            raise ValidationError('Phone number is required.')
        # Additional validation is handled by the model's RegexValidator
        return phone_number
    
    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')
        if not date_of_birth:
            raise ValidationError('Date of birth is required.')
        
        from datetime import date
        today = date.today()
        age = today.year - date_of_birth.year - (
            (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
        )
        
        if age < 18:
            raise ValidationError('You must be at least 18 years old to register.')
        
        return date_of_birth
    
    def clean_city(self):
        city = self.cleaned_data.get('city')
        if not city or len(city.strip()) == 0:
            raise ValidationError('City is required.')
        return city.strip()
    
    def clean_state_region(self):
        state_region = self.cleaned_data.get('state_region')
        if not state_region or len(state_region.strip()) == 0:
            raise ValidationError('State/Region is required.')
        return state_region.strip()
    
    def clean_profile_photo(self):
        profile_photo = self.cleaned_data.get('profile_photo')
        if profile_photo:
            # Check file size (max 5MB)
            if profile_photo.size > 5 * 1024 * 1024:
                raise ValidationError('Profile photo must not exceed 5MB.')
        return profile_photo
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        # Validate password strength
        if password:
            strength_errors = self.validate_password_strength(password)
            if strength_errors:
                raise ValidationError({'password': strength_errors})
        
        # Check password confirmation
        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError({'confirm_password': 'Passwords do not match.'})
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        user.set_password(password)
        user.terms_accepted = True
        user.terms_accepted_at = timezone.now()
        
        if commit:
            user.save()
        
        return user


class UserLoginForm(forms.Form):
    """Form for user login."""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Remember Me'
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise ValidationError('Invalid email or password.')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        
        if email and password:
            try:
                user = CustomUser.objects.get(email=email)
                
                # Check if account is locked
                if user.is_account_locked():
                    raise ValidationError(
                        'Your account has been locked due to multiple failed login attempts. '
                        'Please try again later.'
                    )
                
                # Check password
                if not user.check_password(password):
                    user.record_failed_login()
                    raise ValidationError('Invalid email or password.')
                
            except CustomUser.DoesNotExist:
                raise ValidationError('Invalid email or password.')
        
        return cleaned_data


class ForgotPasswordForm(forms.Form):
    """Form for requesting password reset."""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            # Don't reveal if email exists in system
            pass
        return email


class ResetPasswordForm(PasswordStrengthMixin, forms.Form):
    """Form for resetting password with token."""
    
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New Password (min 8 chars, uppercase, lowercase, number)',
        }),
        help_text='Minimum 8 characters, must include uppercase, lowercase, and number'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm New Password'
        })
    )
    
    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            errors = self.validate_password_strength(new_password)
            if errors:
                raise ValidationError(errors)
        return new_password
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise ValidationError({'confirm_password': 'Passwords do not match.'})
        
        return cleaned_data
