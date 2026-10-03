from django import template

register = template.Library()


@register.filter
def split(value, arg=","):
    return str(value).split(arg)


@register.filter
def split_lines(value):
    return str(value).splitlines()
