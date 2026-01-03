import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ppl.settings')
import django
django.setup()
from django.core.mail import send_mail
from django.conf import settings
print('Email Settings:')
print(f'Backend: {settings.EMAIL_BACKEND}')
print(f'Host: {settings.EMAIL_HOST}')
print(f'User: {settings.EMAIL_HOST_USER}')
print(f'From: {settings.DEFAULT_FROM_EMAIL}')
print('Testing email send...')
try:
    result = send_mail(
        'Test Email from P2P Solutions',
        'This is a test email to verify email configuration.',
        settings.DEFAULT_FROM_EMAIL,
        ['soarersavannah@gmail.com'],
        fail_silently=False,
    )
    print(f'\u2713 Email sent successfully! Result: {result}')
except Exception as e:
    print(f'\u2717 Error: {type(e).__name__}: {e}')
