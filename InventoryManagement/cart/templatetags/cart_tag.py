from django import template

register = template.Library()

@register.filter()
def multiply(value, arg):
    """Multiply the value by arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0  # Return 0 if there is an error in conversion

@register.filter()
def add(value, arg):
    """Add arg to the value."""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return 0  # Return 0 if there is an error in conversion

@register.filter()
def tax(value, tax_value=0.0275):
    """Add tax value to the value."""
    return float(value) * float(tax_value)