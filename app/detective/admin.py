from django.contrib import admin
from app.detective.models import QuoteRequest

class QuoteRequestAdmin(admin.ModelAdmin):
    list_filter = ("employer", "records", "users", "public", )
    search_fields = ("name", "employer", "domain", "email", "comment",)

admin.site.register(QuoteRequest, QuoteRequestAdmin)