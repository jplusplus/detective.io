from django import template
register = template.Library()

@register.filter('klass')
def klass(ob):
    return ob.__class__.__name__


@register.filter('queryset_klass')
def queryset_klass(ob):
    return ob.field.queryset.model.__name__
    

@register.filter('field_to_type')
def field_to_type(field):	
	model  = field.form.Meta.model
	fields = model._meta.fields
	matches = [f for f in fields if f.name == field.name]		
	return matches[0].get_internal_type() if len(matches) else None