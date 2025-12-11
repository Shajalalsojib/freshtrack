from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def expiry_timestamp(product):
    """Convert expiry datetime to JavaScript timestamp in milliseconds"""
    if product.expiry_datetime:
        return int(product.expiry_datetime.timestamp() * 1000)
    return 0

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Get item from dictionary with integer key"""
    try:
        return dictionary.get(int(key), 0)
    except:
        return 0

@register.filter
def urgency_level(expiry_datetime):
    """
    Calculate urgency level based on expiry time
    Returns: 'expired', 'critical', 'urgent', 'warning', 'normal', or 'fresh'
    """
    if not expiry_datetime:
        return 'normal'
    
    now = timezone.now()
    
    # Already expired
    if expiry_datetime < now:
        return 'expired'
    
    # Calculate time remaining
    time_left = expiry_datetime - now
    hours_left = time_left.total_seconds() / 3600
    days_left = time_left.days
    
    # Less than 1 hour (critical)
    if hours_left < 1:
        return 'critical'
    
    # Less than 24 hours (urgent)
    elif days_left == 0:
        return 'urgent'
    
    # 1-3 days (warning)
    elif days_left <= 3:
        return 'warning'
    
    # 4-7 days (normal)
    elif days_left <= 7:
        return 'normal'
    
    # More than 7 days (fresh)
    else:
        return 'fresh'
