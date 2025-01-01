# inventory/templatetags/custom_tags.py
from django import template
from e_commerce.models import Order

register = template.Library()

# Define an inclusion tag that counts the number of orders with seen_by_user=False
@register.simple_tag
def counter():
    # Get the count of orders where 'seen_by_user' is False
    count = Order.objects.filter(seen_by_user=False).count()
    
    # Return the count as the result of the tag
    return count