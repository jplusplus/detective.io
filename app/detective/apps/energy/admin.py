from neo4django             import admin
from .models     			import *

class EnergyProjectAdmin(admin.ModelAdmin): pass
admin.site.register(EnergyProject, EnergyProjectAdmin)

class EnergyProductAdmin(admin.ModelAdmin): pass
admin.site.register(EnergyProduct, EnergyProductAdmin)
