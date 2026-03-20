from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply two numbers"""
    return value * arg

@register.filter
def sum_total(items):
    """Sum total of quantity * price for all items"""
    return sum(item.quantity * item.price for item in items)