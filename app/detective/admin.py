from app.detective        import utils
from app.detective.models import QuoteRequest, Topic, SearchTerm, Article
from django.conf          import settings
from django.contrib       import admin
from django.db.models     import CharField

class QuoteRequestAdmin(admin.ModelAdmin):
    save_on_top   = True
    list_filter   = ("employer", "records", "users", "public", )
    search_fields = ("name", "employer", "domain", "email", "comment",)

admin.site.register(QuoteRequest, QuoteRequestAdmin)

# Display relationship admin panel only on debug mode
if settings.DEBUG:
    class SearchTermAdmin(admin.ModelAdmin):
        list_display  = ("name", "label", "subject", "topic", "is_literal",)
    admin.site.register(SearchTerm, SearchTermAdmin)


class SearchTermInline(admin.TabularInline):
    model  = SearchTerm
    extra  = 0

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'name':
            # We add temporary choices for this field so
            # it will be threaded as a selectbox
            choices = ( (None, "Will be replaced"), )
            db_field = CharField(
                name=db_field.name,
                verbose_name=db_field.verbose_name,
                primary_key=db_field.primary_key,
                max_length=db_field.max_length,
                blank=db_field.blank,
                rel=db_field.rel,
                default=db_field.default,
                editable=db_field.editable,
                serialize=db_field.serialize,
                unique_for_date=db_field.unique_for_date,
                unique_for_year=db_field.unique_for_year,
                help_text=db_field.help_text,
                db_column=db_field.db_column,
                db_tablespace=db_field.db_tablespace,
                auto_created=db_field.auto_created,
                db_index=db_field.db_index,
                validators=db_field.validators,
                # The ony field we don't copy
                choices=choices
            )

        return super(SearchTermInline, self).formfield_for_dbfield(db_field, **kwargs)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'name' and hasattr(request, "topic_id"):
            # We add choices for this field using the current topic's models
            kwargs["choices"] = []
            # Get the current topic with the ID set into the parent form
            topic  = Topic.objects.get(id=request.topic_id)
            # Get the topic's models
            models = topic.get_models()
            for model in models:
                model_name    = getattr(model._meta, "verbose_name").title()
                subset        = []
                # Retreive every relationship field for this model
                for field in utils.get_model_fields(model):
                    if field["type"] != 'AutoField':
                        choice   = [ field["name"], field["verbose_name"].title(), ]
                        # Add ... at the end ot the relationship field
                        if field["type"] == 'Relationship': choice[1] += "..."
                        subset.append(choice)
                # Add the choice subset only if it contains elements
                if len(subset): kwargs["choices"].append( (model_name, subset,) )
        return super(SearchTermInline, self).formfield_for_choice_field(db_field, request,**kwargs)

class TopicAdmin(admin.ModelAdmin):
    save_on_top         = True
    prepopulated_fields = {'slug': ('title',)}
    list_display        = ("title", "link", "public","app_label",)
    list_filter         = ("public","featured","author")
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields':  (
                ('title', 'slug',),
                ('public',),
                ('featured',),
                ('author',),
            )
        }),
        ('Describe your field of study', {
            'classes': ('wide',),
            'description': 'Choose one of this tree ways to define your ontology.',
            'fields': ( ('ontology_as_mod', 'ontology_as_json', 'ontology_as_owl',))
        }),
        ('Advanced options', {
            'classes': ('wide',),
            'fields': ( 'description', 'about', 'background', )
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        if hasattr(obj, "id"):
            # Save the topic id into the request to retreive it into inline form
            setattr(request, 'topic_id', obj.id)
            # Add inlice SearchTerm only for saved object
            self.inlines = (SearchTermInline,)
        else:
            self.inlines = []
        return super(TopicAdmin, self).get_form(request, obj, **kwargs)


admin.site.register(Topic, TopicAdmin)

class ArticleAdmin(admin.ModelAdmin):
    save_on_top         = True
    prepopulated_fields = {'slug': ('title',)}
    list_display        = ("title", "link", "created_at", "public", )

admin.site.register(Article, ArticleAdmin)