from .models    import *
from neo4django import admin

class CountryAdmin(admin.ModelAdmin): pass
admin.site.register(Country, CountryAdmin)