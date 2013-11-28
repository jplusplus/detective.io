from django.contrib import admin
from app.detective.models import QuoteRequest, Topic

class QuoteRequestAdmin(admin.ModelAdmin):
    list_filter = ("employer", "records", "users", "public", )
    search_fields = ("name", "employer", "domain", "email", "comment",)

admin.site.register(QuoteRequest, QuoteRequestAdmin)

class TopicAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ("title", "link", "public", )
admin.site.register(Topic, TopicAdmin)