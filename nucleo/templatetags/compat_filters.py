from django import template


register = template.Library()


@register.filter(name="length_is")
def length_is(value, arg):
    try:
        expected = int(arg)
    except (TypeError, ValueError):
        return False

    try:
        return len(value) == expected
    except TypeError:
        return False
