from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def get_next_page_url(context, tag=None, query=None, username=None):
    page = context["page_obj"].number + 1
    if tag:
        return f"{reverse('blogs:tag_list', args=[tag])}?page={page}"
    elif query:
        return f"{reverse('blogs:search')}?q={query}&page={page}"
    elif username:
        user = context["user"]
        return f"{user.get_absolute_url()}?page={page}"
    else:
        return f"{reverse('blogs:index')}?page={page}"
