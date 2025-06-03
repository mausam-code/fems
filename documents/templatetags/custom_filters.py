from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    """
    Replaces all instances of the first argument with the second argument in the given value.
    Usage: {{ value|replace:"old,new" }}
    """
    if value is None:
        return ''
    
    try:
        old, new = arg.split(',')
        return value.replace(old, new)
    except (ValueError, AttributeError):
        return value