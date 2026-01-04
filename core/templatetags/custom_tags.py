from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag
def get_home_url(user):
    """
    Get the appropriate home URL based on user certification status.
    Certified users go to office schedule, others go to training dashboard.
    """
    if user and user.is_authenticated:
        try:
            if user.certification and user.certification.is_certified:
                return reverse('core:office-schedule')
        except:
            pass
    
    return reverse('core:training-dashboard')
