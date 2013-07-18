from neo4django import admin
from app.detective.models import Amount, Country, FundraisingRound, Organization, Price, Project, Commentary, Distribution, EnergyProject, InternationalOrganization, Person, Revenue, Company, Fund, Product, EnergyProduct, Ngo
from neo4django.auth.models import User

class UserAdmin(admin.ModelAdmin):
	pass

class AmountAdmin(admin.ModelAdmin):
	pass

class CountryAdmin(admin.ModelAdmin):
	pass

class FundraisingRoundAdmin(admin.ModelAdmin):
	pass

class OrganizationAdmin(admin.ModelAdmin):
	def __unicode__(self):
		return self.name

class PriceAdmin(admin.ModelAdmin):
	pass

class ProjectAdmin(admin.ModelAdmin):
	pass

class CommentaryAdmin(admin.ModelAdmin):
	pass

class DistributionAdmin(admin.ModelAdmin):
	pass

class EnergyProjectAdmin(admin.ModelAdmin):
	pass

class InternationalOrganizationAdmin(admin.ModelAdmin):
	pass

class PersonAdmin(admin.ModelAdmin):
	pass

class RevenueAdmin(admin.ModelAdmin):
	pass

class CompanyAdmin(admin.ModelAdmin):
	pass

class FundAdmin(admin.ModelAdmin):
	pass

class ProductAdmin(admin.ModelAdmin):
	pass

class EnergyProductAdmin(admin.ModelAdmin):
	pass

class NgoAdmin(admin.ModelAdmin):
	pass


admin.site.register(User, UserAdmin)
admin.site.register(Amount, AmountAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(FundraisingRound, FundraisingRoundAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Price, PriceAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Commentary, CommentaryAdmin)
admin.site.register(Distribution, DistributionAdmin)
admin.site.register(EnergyProject, EnergyProjectAdmin)
admin.site.register(InternationalOrganization, InternationalOrganizationAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Revenue, RevenueAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Fund, FundAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(EnergyProduct, EnergyProductAdmin)
admin.site.register(Ngo, NgoAdmin)