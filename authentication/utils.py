"""Utility functions for authentication app."""

import re
import logging

logger = logging.getLogger(__name__)


def get_password_strength_class(password):
    """
    Get CSS class for password strength indicator.
    
    Args:
        password: Password string
        
    Returns:
        Tuple of (strength_level, css_class, description)
    """
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
