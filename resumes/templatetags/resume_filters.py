from django import template

register = template.Library()

@register.filter
def split(value, delimiter):
    """
    Split a string by a delimiter and return the list of parts.
    Usage: {{ value|split:"delimiter" }}
    """
    return value.split(delimiter)

@register.filter
def filename(value):
    """
    Extract filename from a file path.
    Usage: {{ value|filename }}
    """
    # Handle both Windows and Unix-style paths
    for delimiter in ['\\', '/']:
        if delimiter in value:
            value = value.split(delimiter)[-1]
    return value

@register.filter
def file_extension(value):
    """
    Extract file extension from a filename.
    Usage: {{ value|file_extension }}
    """
    if '.' in value:
        return value.split('.')[-1].upper()
    return '' 