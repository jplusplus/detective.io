from django import template
register = template.Library()

@register.filter('klass')
def klass(ob):
    return ob.__class__.__name__