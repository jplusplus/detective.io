from neo4django             import admin
from app.detective.models   import *
from neo4django.auth.models	import User

class UserAdmin(admin.ModelAdmin): pass
admin.site.register(User, UserAdmin)
