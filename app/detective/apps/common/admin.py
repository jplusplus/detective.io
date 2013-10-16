from .models    import *
from neo4django import admin

class AmountAdmin(admin.ModelAdmin): pass
admin.site.register(Amount, AmountAdmin)

class CountryAdmin(admin.ModelAdmin): pass
admin.site.register(Country, CountryAdmin)

class FundraisingRoundAdmin(admin.ModelAdmin): pass
admin.site.register(FundraisingRound, FundraisingRoundAdmin)

class OrganizationAdmin(admin.ModelAdmin): pass
admin.site.register(Organization, OrganizationAdmin)

class PriceAdmin(admin.ModelAdmin): pass
admin.site.register(Price, PriceAdmin)

class ProjectAdmin(admin.ModelAdmin): pass
admin.site.register(Project, ProjectAdmin)

class CommentaryAdmin(admin.ModelAdmin): pass
admin.site.register(Commentary, CommentaryAdmin)

class DistributionAdmin(admin.ModelAdmin): pass
admin.site.register(Distribution, DistributionAdmin)

class PersonAdmin(admin.ModelAdmin): pass
admin.site.register(Person, PersonAdmin)

class RevenueAdmin(admin.ModelAdmin): pass
admin.site.register(Revenue, RevenueAdmin)

class ProductAdmin(admin.ModelAdmin): pass
admin.site.register(Product, ProductAdmin)