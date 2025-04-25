from django import template

register = template.Library()

@register.filter(name='map')
def map_filter(value, arg):
    """
    Apply a mapping operation to an iterable.
    
    Usage:
        {{ my_list|map:"attribute_name" }}
    
    Example:
        {{ jobs_data|map:"total_applications"|sum }}
    """
    try:
        return [getattr(item, arg) if hasattr(item, arg) else item.get(arg) for item in value]
    except (AttributeError, KeyError, TypeError):
        return []

@register.filter(name='test_filter')
def test_filter(value):
    """A simple test filter to verify the template library is loading."""
    return f"TEST: {value}"

@register.filter(name='total_applications_sum')
def total_applications_sum(jobs_data):
    """
    Calculate the sum of total_applications from jobs_data.
    
    Usage:
        {{ jobs_data|total_applications_sum }}
    """
    try:
        return sum(job.total_applications for job in jobs_data)
    except (AttributeError, TypeError):
        return 0

@register.filter(name='pending_applications_count')
def pending_applications_count(jobs_data):
    """
    Count the number of pending applications across all jobs.
    
    Usage:
        {{ jobs_data|pending_applications_count }}
    """
    try:
        return sum(
            len([candidate for candidate in job.top_candidates 
                 if candidate.application.status == 'PENDING'])
            for job in jobs_data
        )
    except (AttributeError, TypeError):
        return 0 