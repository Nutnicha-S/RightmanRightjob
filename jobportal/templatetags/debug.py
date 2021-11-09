from django import template

register = template.Library()

def id(value):
    return value._id

register.filter('id', id)