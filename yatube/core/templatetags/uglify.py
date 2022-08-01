from django import template

register = template.Library()


@register.filter
def uglify(s1):
    s = ''
    for num, data in enumerate(s1):
        if num % 2 == 0:
            s += data.lower()
        else:
            s += data.upper()
    return s
