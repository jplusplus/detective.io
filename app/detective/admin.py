from django.contrib       import admin
from django               import forms
from app.detective.models import QuoteRequest, Topic, RelationshipSearch, Article

class QuoteRequestAdmin(admin.ModelAdmin):
    list_filter = ("employer", "records", "users", "public", )
    search_fields = ("name", "employer", "domain", "email", "comment",)

admin.site.register(QuoteRequest, QuoteRequestAdmin)


class RelationshipSearchForm(forms.ModelForm):
    class Meta:
        pass

class RelationshipSearchInline(admin.TabularInline):
    model = RelationshipSearch
    form  = RelationshipSearchForm
    extra = 1

class TopicAdmin(admin.ModelAdmin):
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
    prepopulated_fields = {'slug': ('title',)}
    list_display = ("title", "link", "created_at", "public", )

admin.site.register(Article, ArticleAdmin)