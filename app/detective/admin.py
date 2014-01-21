from django.contrib       import admin
from app.detective.models import QuoteRequest, Topic, RelationshipSearch, Article

class QuoteRequestAdmin(admin.ModelAdmin):
    save_on_top   = True
    list_filter   = ("employer", "records", "users", "public", )
    search_fields = ("name", "employer", "domain", "email", "comment",)

admin.site.register(QuoteRequest, QuoteRequestAdmin)

class RelationshipSearchInline(admin.TabularInline):
    model = RelationshipSearch
    extra = 1

class TopicAdmin(admin.ModelAdmin):
    save_on_top         = True
    prepopulated_fields = {'slug': ('title',)}
    list_display        = ("title", "link", "public", )
    inlines             = (RelationshipSearchInline,)
    fieldsets = (
        (None, {
            'fields':  ( ('title', 'slug',), 'ontology', 'module', 'public')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ( 'description', 'about', 'background', )
        }),
    )


admin.site.register(Topic, TopicAdmin)

class ArticleAdmin(admin.ModelAdmin):
    save_on_top         = True
    prepopulated_fields = {'slug': ('title',)}
    list_display        = ("title", "link", "created_at", "public", )

admin.site.register(Article, ArticleAdmin)