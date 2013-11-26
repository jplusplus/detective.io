from django.contrib import admin
from app.detective.models import QuoteRequest

class QuoteRequestAdmin(admin.ModelAdmin):
    list_filter = ("employer", "domain", "records", "users", "public", )
    search_fields = ("name", "employer", "email", "comment",)

admin.site.register(QuoteRequest, QuoteRequestAdmin)