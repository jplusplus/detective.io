from neo4django.db import models
# Overload all neo4django's properties to add custom options

class CustomField(object):  
    form_hidden = False
    def __init__(self, form_hidden=False):
        self.form_hidden = form_hidden


class Property(CustomField, models.Property):
    def __init__(self , **kwargs):
        models.Property.__init__(self, **kwargs)



class StringProperty(models.StringProperty):
    hidden_form = False
    def __init__(self, verbose_name=None, name=None, hidden_form=False, **kwargs):
        self.hidden_form = hidden_form
        models.StringProperty.__init__(self, verbose_name, name,**kwargs)



class EmailProperty(CustomField, models.EmailProperty):
    def __init__(self , **kwargs):
        models.EmailProperty.__init__(self, **kwargs)



class URLProperty(CustomField, models.URLProperty):
    def __init__(self , **kwargs):
        models.URLProperty.__init__(self, **kwargs)



class IntegerProperty(CustomField, models.IntegerProperty):
    def __init__(self , **kwargs):
        models.IntegerProperty.__init__(self, **kwargs)



class DateProperty(CustomField, models.DateProperty):
    def __init__(self , **kwargs):
        models.DateProperty.__init__(self, **kwargs)



class DateTimeProperty(CustomField, models.DateTimeProperty):
    def __init__(self , **kwargs):
        models.DateTimeProperty.__init__(self, **kwargs)



class ArrayProperty(CustomField, models.ArrayProperty):
    def __init__(self , **kwargs):
        models.ArrayProperty.__init__(self, **kwargs)



class StringArrayProperty(CustomField, models.StringArrayProperty):
    def __init__(self , **kwargs):
        models.DateField.__init__(self, **kwargs)



class IntArrayProperty(CustomField, models.IntArrayProperty):
    def __init__(self , **kwargs):
        models.IntArrayProperty.__init__(self, **kwargs)



class URLArrayProperty(CustomField, models.URLArrayProperty):
    def __init__(self , **kwargs):
        models.URLArrayProperty.__init__(self, **kwargs)



class AutoProperty(CustomField, models.AutoProperty):
    def __init__(self , **kwargs):
        models.AutoProperty.__init__(self, **kwargs)



class BooleanProperty(CustomField, models.BooleanProperty):
    def __init__(self , **kwargs):
        models.BooleanProperty.__init__(self, **kwargs)


