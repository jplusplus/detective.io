from app.detective        import utils
from app.detective.models import QuoteRequest, Topic, RelationshipSearch, Article
from django.contrib       import admin

class QuoteRequestAdmin(admin.ModelAdmin):
    save_on_top   = True
    list_filter   = ("employer", "records", "users", "public", )
    search_fields = ("name", "employer", "domain", "email", "comment",)

admin.site.register(QuoteRequest, QuoteRequestAdmin)

class RelationshipSearchInline(admin.TabularInline):
    model = RelationshipSearch
    extra = 1

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'name':
            # We add temporary choices for this field so
            # it will be threaded as a selectbox
            choices = ( (None, "Will be replaced"), )
            # This is the way we update the choices attributes
            db_field._choices = choices
        return super(RelationshipSearchInline, self).formfield_for_dbfield(db_field, **kwargs)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'name' and hasattr(request, "topic_id"):
            # We add choices for this field using the current topic's models
            kwargs["choices"] = []
            # Get the current topic with the ID set into the parent form
            topic  = Topic.objects.get(id=request.topic_id)
            # Get the topic's models
            models = utils.get_topic_models(topic)
            for model in models:
                model_name    = getattr(model._meta, "verbose_name").title()
                subset        = []
                # Retreive every relationship field for this model
                for field in utils.get_model_fields(model):
                    if field["type"] == 'Relationship':
                        rel_type = field["rel_type"]
                        choice     = (rel_type, rel_type, )
                        subset.append(choice)
                # Add the choice subset only if it contains elements
                if len(subset): kwargs["choices"].append( (model_name, subset,) )
        return super(RelationshipSearchInline, self).formfield_for_choice_field(db_field, request,**kwargs)

class TopicAdmin(admin.ModelAdmin):
    save_on_top         = True
    prepopulated_fields = {'slug': ('title',)}
    list_display        = ("title", "link", "public", )
    fieldsets = (
        (None, {
            'fields':  ( ('title', 'slug',), 'ontology', 'module', 'public')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ( 'description', 'about', 'background', )
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        if hasattr(obj, "id"):
            # Save the topic id into the request to retreive it into inline form
            setattr(request, 'topic_id', obj.id)
            # Add inlice RelationshipSearch only for saved object
            self.inlines = (RelationshipSearchInline,)
        return super(TopicAdmin, self).get_form(request, obj, **kwargs)


admin.site.register(Topic, TopicAdmin)

class ArticleAdmin(admin.ModelAdmin):
    save_on_top         = True
    prepopulated_fields = {'slug': ('title',)}
    list_display        = ("title", "link", "created_at", "public", )

admin.site.register(Article, ArticleAdmin)