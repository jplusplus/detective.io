from .models	 import *
from neo4django  import admin

class EnergyProjectAdmin(admin.ModelAdmin): pass
admin.site.register(EnergyProject, EnergyProjectAdmin)

class EnergyProductAdmin(admin.ModelAdmin): pass
admin.site.register(EnergyProduct, EnergyProductAdmin)
