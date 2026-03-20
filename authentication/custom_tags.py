from django.template import Library

register = Library()

@register.simple_tag
def sum_two(num_1,num_2):

    return num_1+num_2

@register.simple_tag
def upper_case(word):

    return word.upper()

@register.simple_tag
def check_permission(request,roles):

    role_list = eval(roles)

    return request.user.is_authenticated and request.user.role in role_list


# @register.simple_tag
# def 





