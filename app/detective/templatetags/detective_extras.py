from django import template
register = template.Library()

@register.filter('klass')
def klass(ob):
    return ob.__class__.__name__


@register.filter('queryset_klass')
def queryset_klass(ob):
    return ob.field.queryset.model.__name__
    