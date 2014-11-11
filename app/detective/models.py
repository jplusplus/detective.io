from app.detective              import utils
from app.detective.exceptions   import UnavailableImage
from app.detective.permissions  import create_permissions, remove_permissions
from app.detective.parser       import schema

from django                     import forms
from django.conf                import settings
from django.contrib.auth.models import User, Group
from django.core.cache          import cache
from django.core.paginator      import Paginator
from django.db                  import models
from django.db.models           import signals
from django.utils.text          import slugify
from django.utils.html          import strip_tags

from jsonfield                  import JSONField
from jsonschema                 import validate
from jsonschema.exceptions      import ValidationError
from neo4django.db              import connection
from tinymce.models             import HTMLField

import hashlib
import importlib
import inspect
import os
import random
import re
import string
import urllib2
import django_rq
import base64

# -----------------------------------------------------------------------------
#
#    CHOICES & ENUMERATIONS & DICTS
#
# -----------------------------------------------------------------------------
PUBLIC = (
    (True, "Yes, public"),
    (False, "No, just for a small group of users"),
)

FEATURED = (
    (True, "Yes, show it on the homepage"),
    (False, "No, stay out of the ligth"),
)

PLANS_CHOICES = [(d[:10], d) for p in settings.PLANS for d in p.keys()]
PLANS_BY_NAMES = dict([d for p in settings.PLANS for d in p.items()])

class QuoteRequest(models.Model):
    RECORDS_SIZE = (
        (0, "Less than 200"),
        (200, "Between 200 and 1000"),
        (1000, "Between 1000 & 10k"),
        (10000, "More than 10k"),
        (-1, "I don't know yet"),
    )
    USERS_SIZE = (
        (1, "1"),
        (5, "1-5"),
        (0, "More than 5"),
        (-1, "I don't know yet"),
    )
    name     = models.CharField(max_length=100)
    employer = models.CharField(max_length=100)
    email    = models.EmailField(max_length=100)
    phone    = models.CharField(max_length=100, blank=True, null=True)
    domain   = models.TextField(help_text="Which domain do you want to investigate on?")
    records  = models.IntegerField(choices=RECORDS_SIZE, blank=True, null=True, help_text="How many entities do you plan to store?")
    users    = models.IntegerField(choices=USERS_SIZE, blank=True, null=True, help_text="How many people will work on the investigation?")
    public   = models.NullBooleanField(choices=PUBLIC, null=True, help_text="Will the data be public?")
    comment  = models.TextField(blank=True, null=True, help_text="Anything else you want to tell us?")

    def __unicode__(self):
        return "%s - %s" % (self.name, self.email,)

def validate_ontology_as_json(value):
    try:
        # For retro-compatibility, we do not validate object-like ontologies
        if type(value) is list:
            # First, validate the ontology format
            validate(value, schema.ontology, format_checker=schema.checker(value))
    except ValidationError, e:
        raise forms.ValidationError(e.message)

class TopicSkeleton(models.Model):
    title           = models.CharField(max_length=250, help_text="Title of the skeleton")
    description     = HTMLField(null=True, blank=True, help_text="A small description of the skeleton")
    picture         = models.ImageField(upload_to="topics-skeletons", null=True, blank=True, help_text='The default picture for this skeleton')
    picture_credits = models.CharField(max_length=250, help_text="Enter the proper credits for the chosen skeleton picture", null=True, blank=True)
    schema_picture  = models.ImageField(upload_to="topics-skeletons", null=True, blank=True,  help_text='A picture illustrating how data is modelized')
    ontology        = JSONField(null=True, verbose_name=u'Ontology (JSON)', blank=True)
    target_plans    = models.CharField(max_length=60)
    tutorial_link   = models.URLField(null=True, blank=True, help_text='A link to the tutorial video/article for this data scheme')
    enable_teasing  = models.BooleanField(default=False, help_text='Show this skeleton as a teasing skeleton for free user')
    order           = models.PositiveIntegerField()

    def description_stripped(self):
        return strip_tags(self.description)


    def selected_plans(self):
        selected_plans = []
        for plan in PLANS_CHOICES:
            if plan[0] in self.target_plans:
                selected_plans.append(plan[0])
        return selected_plans

    @property
    def ontology_models(self):
        return [ m["verbose_name"] for m in self.ontology if "verbose_name" in m ]

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["order", "title"]

class TopicDataSet(models.Model):
    title = models.CharField(max_length=250, help_text="Title of the dataset")
    description = HTMLField(null=True, blank=True, help_text="A small description of the dataset")
    picture = models.ImageField(upload_to="topics-dataset/pictures", null=True, blank=True, help_text='Picture for this dataset')
    target_plans = models.CharField(max_length=60)
    target_skeletons = models.ManyToManyField(TopicSkeleton, related_name="datasets")
    zip_file = models.FileField(upload_to="topics-dataset/zips", help_text='The actual dataset', null=True, blank=True)

    def description_stripped(self):
        return strip_tags(self.description)

    def selected_skeletons(self):
        return [x.__str__() for x in self.target_skeletons.all()]

    def selected_plans(self):
        selected_plans = []
        for plan in PLANS_CHOICES:
            if plan[0] in self.target_plans:
                selected_plans.append(plan[0])
        return selected_plans

class Topic(models.Model):
    background_upload_to='topics'
    class Meta:
        unique_together = (
            ('slug','author')
        )
    title            = models.CharField(max_length=250, help_text="Title of your topic.")
    skeleton_title   = models.CharField(max_length=250, null=True, blank=True)
    # Value will be set for this field if it's blank
    slug             = models.SlugField(max_length=250, db_index=True, help_text="Token to use into the url.")
    description      = HTMLField(null=True, blank=True, verbose_name='subtitle', help_text="A short description of what is your topic.")
    about            = HTMLField(null=True, blank=True, help_text="A longer description of what is your topic.")
    public           = models.BooleanField(help_text="Is your topic public?", default=True, choices=PUBLIC)
    featured         = models.BooleanField(help_text="Is your topic a featured topic?", default=False, choices=FEATURED)
    background       = models.ImageField(null=True, blank=True, upload_to=background_upload_to, help_text="Background image displayed on the topic's landing page.")
    author           = models.ForeignKey(User, help_text="Author of this topic.", null=True)
    contributor_group   = models.ForeignKey(Group, help_text="", null=True, blank=True)
    administrator_group = models.ForeignKey(Group, help_text="", null=True, blank=True, related_name='admin_topic')

    ontology_as_owl  = models.FileField(null=True, blank=True, upload_to="ontologies", verbose_name="Ontology as OWL", help_text="Ontology file that descibes your field of study.")
    ontology_as_mod  = models.SlugField(blank=True, max_length=250, verbose_name="Ontology as a module", help_text="Module to use to create your topic.")
    ontology_as_json = JSONField(null=True, verbose_name="Ontology as JSON", blank=True, validators=[validate_ontology_as_json])

    dataset = models.ForeignKey(TopicDataSet, blank=True, null=True)

    def __unicode__(self):
        return self.title

    def get_contributor_group(self):
        try:
            return Group.objects.get(name="%s_contributor" % self.app_label())
        except Group.DoesNotExist:
            create_permissions(self.get_module(), app_label=self.ontology_as_mod)
            return Group.objects.get(name="%s_contributor" % self.app_label())

    def app_label(self):
        if self.slug in ["common", "energy"] and self.author and self.author.username == 'detective':
            return self.slug
        elif not self.ontology_as_mod:
            # Already saved topic
            if self.id:
                cache_key = "prefetched_topic_%s" % self.id
                # Store topic object in a temporary attribute
                # to avoid SQL lazyness
                if getattr(self, cache_key, None) is None:
                    topic = Topic.objects.get(id=self.id)
                    setattr(self, cache_key, topic)
                else:
                    topic = getattr(self, cache_key)
                # Restore the previous ontology_as_mod value
                self.ontology_as_mod = topic.ontology_as_mod
                # Call this function again.
                # Continue if ontology_as_mod is still empty
                if self.ontology_as_mod: return self.app_label()
            while True:
                token = Topic.get_module_token()
                # Break the loop only if the token doesn't exist
                if not Topic.objects.filter(ontology_as_mod=token).exists(): break
            # Save the new token
            self.ontology_as_mod = token
        return self.ontology_as_mod

    @staticmethod
    def get_module_token(size=10, chars=string.ascii_uppercase + string.digits):
        return "topic%s" % ''.join(random.choice(chars) for x in range(size))

    def get_module(self):
        from app.detective import topics
        return getattr(topics, self.app_label())

    def get_models_module(self):
        """ return the module topic_module.models """
        return getattr(self.get_module(), "models", {})

    def get_models(self):
        """ return a generator of Model """
        # We have to load the topic's model
        models_module = self.get_models_module()
        for i in dir(models_module):
            klass = getattr(models_module, i)
            # Collect every Django's model subclass
            if inspect.isclass(klass) and issubclass(klass, models.Model):
                yield klass

    def clean(self):
        models.Model.clean(self)

    def save(self, *args, **kwargs):
        # Ensure that the module field is populated with app_label()
        self.ontology_as_mod = self.app_label()

        # For automatic slug generation.
        if not self.slug:
            self.slug = slugify(self.title)[:50]

        # Call the parent save method
        super(Topic, self).save(*args, **kwargs)
        # Refresh the API
        #self.reload()

    def reload(self):
        from app.detective.register import topic_models
        # Register the topic's models again
        topic_models(self.get_module().__name__, force=True)

    def has_default_ontology(self):
        try:
            module = self.get_module()
        except ValueError: return False
        # File if it's a virtual module
        if not hasattr(module, "__file__"): return False
        directory = os.path.dirname(os.path.realpath( module.__file__ ))
        # Path to the ontology file
        ontology  = "%s/ontology.owl" % directory
        return os.path.exists(ontology) or hasattr(self.get_module(), "models")

    def get_absolute_path(self):
        if self.author is None:
            return None
        else:
            return "/%s/%s" % (self.author.username, self.slug,)

    def get_absolute_url(self): return self.get_absolute_path()

    def link(self):
        path = self.get_absolute_path()
        if path is None:
            return ''
        else:
            return '<a href="%s">%s</a>' % (path, path, )

    link.allow_tags = True

    @property
    def search_placeholder(self, max_suggestion=5):
        from app.detective import register
        # Get the model's rules manager
        rulesManager = self.get_rules()
        # List of searchable models
        searchableModels = []
        # Filter searchable models
        for model in self.get_models():
            if rulesManager.model(model).all().get("is_searchable", False):
                searchableModels.append(model)
        names = [ unicode(sm._meta.verbose_name_plural) for sm in searchableModels ]
        random.shuffle(names)
        # No more than X names
        if len(names) > max_suggestion:
            names = names[0:max_suggestion]
        if len(names):
            return "Search for " + ", ".join(names[0:-1]) + " and " + names[-1]
        else:
            return "Search..."

    @property
    def module(self):
        return self.ontology_as_mod

    def entities_count(self):
        """

        Return the number of entities in the current topic.
        Used to inform administrator.
        Expensive request. Cached a long time.

        """
        if not self.id: return 0
        cache_key = "entities_count"
        response = utils.topic_cache.get(self, cache_key)
        if response is None:
            query = """
                START a = node(0)
                MATCH a-[`<<TYPE>>`]->(b)--> c
                WHERE b.app_label = "{app_label}"
                AND not(has(c._relationship))
                RETURN count(c) as count;
            """.format(app_label=self.app_label())
            response = connection.cypher(query).to_dicts()[0].get("count")
            utils.topic_cache.set(self, cache_key, response, 60*60*12) # cached 12 hours
        return response

    def get_syntax(self):
        def syntax_output(m) : return {'name': m.__name__, 'label': m._meta.verbose_name.title()}
        def output(m)        : return {'name': m.name, 'label': m.label, 'subject': m.subject}
        def iterate_fields(model, is_relationship):
            for field in [f for f in utils.iterate_model_fields(model) if (f['type'].lower() == 'relationship') == is_relationship]:
                if "search_terms" in field["rules"]:
                    yield [{'name': field['name'], 'label': st, 'subject': model._meta.object_name} for st in field["rules"]["search_terms"]]
        def output_terms(terms, is_relationship):
            _out = []
            for model in self.get_models():
                _out = list(iterate_fields(model, is_relationship))
            return _out + [ output(rs) for rs in terms ]

        relationship_terms  = (st for st in SearchTerm.objects.filter(topic=self).prefetch_related('topic') if not st.is_literal)
        literal_terms       = (st for st in SearchTerm.objects.filter(topic=self).prefetch_related('topic') if st.is_literal)
        # output
        syntax  = {
            'subject': {
                'model': [ syntax_output(m) for m in self.get_models() if not hasattr(m, "_is_composite") or not m._is_composite ]
            },
            'predicate': {
                'relationship': list(output_terms(relationship_terms, True )),
                'literal'     : list(output_terms(literal_terms     , False))
            }
        }
        return syntax

    def is_registered_literal(self, name):
        literals = self.get_syntax().get("predicate").get("literal")
        matches  = [ literal for literal in literals if name == literal["name"] ]
        return len(matches)

    def is_registered_relationship(self, name):
        literals = self.get_syntax().get("predicate").get("relationship")
        matches  = [ literal for literal in literals if name == literal["name"] ]
        return len(matches)

    def rdf_search_query(self, subject, predicate, obj):
        identifier = obj["id"] if "id" in obj else obj
        # retrieve all models in current topic
        all_models = dict((model.__name__, model) for model in self.get_models())
        # If the received identifier describe a literal value
        if self.is_registered_literal(predicate["name"]):
            # Get the field name into the database
            field_name = predicate["name"]
            # Build the request
            query = """
                START root=node(*)
                MATCH (root)<-[:`<<INSTANCE>>`]-(type)
                WHERE HAS(root.name)
                AND HAS(root.{field})
                AND root.{field} = {value}
                AND type.model_name = {model}
                AND type.app_label = '{app}'
                RETURN DISTINCT ID(root) as id, root.name as name, type.model_name as model
            """.format(
                field=ield_name,
                value=identifier,
                model=subject["name"],
                app=self.app_label()
            )
            print query
        # If the received identifier describe a literal value
        elif self.is_registered_relationship(predicate["name"]):
            fields        = utils.iterate_model_fields( all_models[predicate["subject"]] )
            # Get the field name into the database
            relationships = [ field for field in fields if field["name"] == predicate["name"] ]
            # We didn't find the predicate
            if not len(relationships): return {'errors': 'Unkown predicate type'}
            relationship  = relationships[0]["rel_type"]
            # Query to get every result
            query = u"""
                START st=node({id})
                MATCH (st){is_out}-[:`{relationship}`]-{is_in}(root)<-[:`<<INSTANCE>>`]-(type)
                WHERE HAS(root.name)
                AND HAS(st.name)
                AND type.app_label = '{app}'
                RETURN DISTINCT ID(root) as id, root.name as name, type.model_name as model
            """.format(
                relationship=relationship,
                id=identifier,
                app=self.app_label(),
                is_out='<' if relationships[0]['direction'] == 'out' else '',
                is_in='>' if relationships[0]['direction'] == 'in' else ''
            )
            print query
        else:
            return {'errors': 'Unkown predicate type: %s' % predicate["name"]}
        return connection.cypher(query).to_dicts()

    def rdf_search(self, query, limit=20, offset=0):
        subject   = query.get("subject", None)
        predicate = query.get("predicate", None)
        obj       = query.get("object", None)
        results   = self.rdf_search_query(subject, predicate, obj)
        # Stop now in case of error
        if "errors" in results: return results
        paginator = Paginator(results, limit)
        if offset < 0:
            p = -1
        else:
            p = int(round(offset / limit)) +  1
        page      = paginator.page(p)
        objects   = []
        for result in page.object_list:
            objects.append(result)
        return {
            'objects': objects,
            'meta': {
                'q': query,
                'offset': p,
                'limit': limit,
                'total_count': paginator.count
            }
        }

    def get_rules(self):
        from app.detective.modelrules import ModelRules
        from app.detective.register   import TopicRegistor
        # ModelRules is a singleton that record every model rules
        rules = ModelRules()
        registor = TopicRegistor()
        registor.register_topic(self)
        # Does this app contain a forms.py file?
        path = "app.detective.topics.%s.forms" % self.ontology_as_mod
        try:
            mod  = importlib.import_module(path)
        except ImportError:
            # Ignore absent forms.py
            return rules
        func = getattr(mod, "topics_rules", None)
        # Simply call the function to register app's rules
        if func: rules = func()
        return rules

class TopicToken(models.Model):
    topic      = models.ForeignKey(Topic, help_text="The topic this token is related to.")
    token      = models.CharField(editable=False, max_length=32, help_text="Title of your article.", db_index=True)
    email      = models.CharField(max_length=255, default=None, null=True, help_text="Email to invite.")
    created_at = models.DateTimeField(auto_now_add=True, default=None, null=True)

    class Meta:
        unique_together = ('topic', 'email',)

    @staticmethod
    def get_random_token(size=32, chars=string.ascii_letters + string.digits):
        return ''.join(random.choice(chars) for x in range(size))

    def save(self):
        if not self.id:
            self.token = self.get_random_token()
            try:
                TopicToken.objects.get(topic=self.topic, token=self.token)
                # Recurcive call to regenerate a random token
                return self.save()
            except TopicToken.DoesNotExist:
                # The topic token MUST not exist yet
                pass
        super(TopicToken, self).save()

class Article(models.Model):
    topic      = models.ForeignKey(Topic, help_text="The topic this article is related to.")
    title      = models.CharField(max_length=250, help_text="Title of your article.")
    slug       = models.SlugField(max_length=250, unique=True, help_text="Token to use into the url.")
    content    = HTMLField(null=True, blank=True)
    public     = models.BooleanField(default=False, help_text="Is your article public?")
    created_at = models.DateTimeField(auto_now_add=True, default=None, null=True)

    def get_absolute_path(self):
        return self.topic.get_absolute_path() + ( "p/%s/" % self.slug )

    def __unicode__(self):
        return self.title

    def link(self):
        path = self.get_absolute_path()
        return '<a href="%s">%s</a>' % (path, path, )
    link.allow_tags = True

class Subscription(models.Model):
    TYPES = (
        ("mr", "Mr."),
        ("ms", "Ms."),
        ("company", "Company")
    )
    PLANS = (
        ("jane", "Jane"),
        ("hank", "Hank"),
        ("sherlock", "Sherlock")
    )
    STATUSES = (
        (0, "..."),
        (1, "Invoice sent"),
        (2, "Processed")
    )
    email = models.EmailField(max_length=100, blank=True, null=True)
    user =  models.ForeignKey(User, null=True, blank=True)
    type = models.CharField(choices=TYPES, max_length=7)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    siret = models.CharField(max_length=20, blank=True, null=True)
    vat = models.CharField(max_length=20, blank=True, null=True)
    identification = models.CharField(max_length=20, blank=True, null=True)
    plan = models.CharField(choices=PLANS, max_length=8)
    status = models.IntegerField(choices=STATUSES, default=0)

# This model aims to describe a research alongside a relationship.
class SearchTerm(models.Model):
    # This field is deduced from the relationship name
    subject    = models.CharField(null=True, blank=True, default='', editable=False, max_length=250, help_text="Kind of entity to look for (Person, Organization, ...).")
    # This field is set automaticly too according the choosen name
    is_literal = models.BooleanField(editable=False, default=False)
    # Every field are required
    label      = models.CharField(null=True, blank=True, default='', max_length=250, help_text="Label of the relationship (typically, an expression such as 'was educated in', 'was financed by', ...).")
    # This field will be re-written by app.detective.admin
    # to be allow dynamic setting of the choices attribute.
    name       = models.CharField(max_length=250, help_text="Name of the relationship inside the subject.")
    topic      = models.ForeignKey(Topic, help_text="The topic this relationship is related to.")

    def find_subject(self):
        subject = None
        # Retreive the subject that match with the instance's name
        field = self.field
        # If any related_model is given, that means its subject is is parent model
        if field is not None:
            subject = field["model"]
            return subject
        else:
            return None

    def clean(self):
        self.subject    = self.find_subject()
        self.is_literal = self.type == "literal"
        models.Model.clean(self)

    @property
    def field(self):
        cache_key = "%s__field" % (self.name)
        field     = utils.topic_cache.get(self.topic, cache_key)
        if field is None and self.name:
            topic_models = self.topic.get_models()
            for model in topic_models:
                # Retreive every relationship field for this model
                for f in utils.iterate_model_fields(model):
                    if f["name"] == self.name:
                        field = f
            field["rules"]["through"] = None # Yes, this is ugly but this field is creating Pickling errors.
            utils.topic_cache.set(self.topic, cache_key, field)
        return field

    @property
    def type(self):
        field = self.field
        if field is None:
            return None
        elif field["type"] == "Relationship":
            return "relationship"
        else:
            return "literal"

    @property
    def target(self):
        if 'related_model' in self.field:
            return self.field["related_model"]
        else:
            return None

# -----------------------------------------------------------------------------
#
#    CUSTOM USER
#
# -----------------------------------------------------------------------------
class DetectiveProfileUser(models.Model):
    user = models.OneToOneField(User)
    plan = models.CharField(max_length=10, choices=PLANS_CHOICES, default=PLANS_CHOICES[0][0])

    location = models.CharField(max_length=100, null=True, blank=True)
    organization = models.CharField(max_length=100, null=True, blank=True)
    url = models.CharField(max_length=100, null=True, blank=True)

    @property
    def avatar(self):
        hash_email = hashlib.md5(self.user.email.strip().lower()).hexdigest()
        return "http://www.gravatar.com/avatar/{hash}?s=200&d=mm".format(
            hash=hash_email)

    def topics_count (self): return Topic.objects.filter(author=self.user).count()
    def topics_max   (self):
        if self.user.is_superuser:
            return -1
        else:
            return PLANS_BY_NAMES[self.get_plan_display()]["max_investigation"]
    def nodes_max    (self):
        if self.user.is_superuser:
            return -1
        else:
            return PLANS_BY_NAMES[self.get_plan_display()]["max_entities"]
    # NOTE: Very expensive if cache is disabled
    def nodes_count  (self): return dict([(topic.slug, topic.entities_count()) for topic in self.user.topic_set.all()])

# -----------------------------------------------------------------------------
#
#    SIGNALS
#
# -----------------------------------------------------------------------------
def update_permissions(*args, **kwargs):
    """ create the permissions related to the label module """
    assert kwargs.get('instance')
    # @TODO check that the slug changed or not to avoid permissions hijacking
    if kwargs.get('created', False):
        create_permissions(kwargs.get('instance').get_module(), app_label=kwargs.get('instance').ontology_as_mod)
    else:
        topic = kwargs.get('instance')
        group_name = '%s_contributor' % topic.ontology_as_mod
        # Update permission only if a author is given
        if topic.author is not None:
            try:
                topic.author.groups.get(name=group_name)
            except Group.DoesNotExist:
                try:
                    topic.author.groups.add(Group.objects.get(name=group_name))
                    topic.author.save()
                except Group.DoesNotExist:
                    pass
                    # Should never get there.

def user_created(*args, **kwargs):
    """

    create a DetectiveProfileUser when a user is created

    """
    DetectiveProfileUser.objects.get_or_create(user=kwargs.get('instance'))

def update_topic_cache(*args, **kwargs):
    """

    update the topic cache version on topic update or sub-model update

    """
    instance = kwargs.get('instance')
    if not isinstance(instance, Topic):
        try:
            topic = utils.get_topic_from_model(instance)
        except Topic.DoesNotExist:
            topic = None
    else:
        topic = instance
    if topic:
        # if topic just been created we gonna bind its sub models signals
        if isinstance(instance, Topic) and kwargs.get('created'):
            utils.topic_cache.init_version(topic)
            for Model in topic.get_models():
                signals.post_save.connect(update_topic_cache, sender=Model, weak=False)
        else:
            # we increment the cache version of this topic, this will "invalidate" every
            # previously stored information related to this topic
            utils.topic_cache.incr_version(topic)

def delete_entity(*args, **kwargs):
    fields = utils.iterate_model_fields(kwargs.get('instance').__class__)
    for field in fields:
        if field["rel_type"] and "through" in field["rules"] and field["rules"]["through"] != None:
            Properties = field["rules"]["through"]
            for info in Properties.objects.all():
                info.delete()
    update_topic_cache(*args, **kwargs)

def apply_dataset(*args, **kwargs):
    assert kwargs.get('instance') # We need an instance...
    if kwargs.get('created', False): # We apply the dataset only on creation
        instance = kwargs.get('instance')
        dataset = getattr(instance, 'dataset', None)
        if dataset != None:
            if dataset.zip_file != None and dataset.zip_file != "":
                from app.detective.topics.common.jobs import unzip_and_process_bulk_parsing_and_save_as_model
                dataset.zip_file.open('r')
                # enqueue the parsing job
                queue = django_rq.get_queue('default', default_timeout=7200)
                job   = queue.enqueue(unzip_and_process_bulk_parsing_and_save_as_model, instance, base64.b64encode(dataset.zip_file.read()))
                dataset.zip_file.close()


signals.post_save.connect(user_created         , sender=User)
signals.post_save.connect(update_topic_cache   , sender=Topic)
signals.post_save.connect(update_permissions   , sender=Topic)
signals.post_save.connect(apply_dataset        , sender=Topic)
signals.post_delete.connect(update_topic_cache , sender=Topic)
signals.post_delete.connect(remove_permissions , sender=Topic)

if getattr(settings, 'ENABLE_PROFILING', False):
    from django.core.signals import request_started, request_finished
    import time

    def start(sender, **kwargs):
        from app.detective.utils import dumb_profiler
        dumb_profiler.started = time.time()

    def finished(sender, **kwargs):
        from app.detective.utils import dumb_profiler
        if getattr(dumb_profiler, 'serializer_time', None):
            total = time.time() - dumb_profiler.started
            api_view_time = dumb_profiler.serializer_time + dumb_profiler.db_time
            request_response_time = dumb_profiler.dispatch_time - dumb_profiler.started

            print ("Database lookup               | %.4fs" % dumb_profiler.db_time)
            print ("Serialization                 | %.4fs" % dumb_profiler.serializer_time)
            print ("Django request/response       | %.4fs" % request_response_time)
            print ("API view                      | %.4fs" % api_view_time)
            print ("Total                         | %.4fs" % total)

            dumb_profiler.new()

    request_started.connect(start)
    request_finished.connect(finished)

# EOF
