"""
Custom template tags and filters shared across all web templates.
"""

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def active_link(context, url_name, css_class="active"):
    """
    Returns `css_class` if the current request matches the given URL name.
    Usage: {% active_link 'store:home' %}
    """
    request = context.get("request")
    if request and getattr(request.resolver_match, "url_name", None) == url_name:
        return css_class
    return ""
