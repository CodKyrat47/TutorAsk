from django import template
from urllib.parse import urlencode

register = template.Library()


@register.simple_tag
def build_paginated_url(request, page_number):
    params = request.GET.copy()
    params['page'] = page_number
    return '?' + urlencode(params)
