from .utils                 import get_topics
from django.db              import models
from django.core.exceptions import ValidationError
import importlib
import os

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
    PUBLIC = (
        (True, "Yes, public"),
        (False, "No, just for a small group of users"),
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

class Topic(models.Model):
    MODULES     = tuple( (topic, topic,) for topic in get_topics() )
    title       = models.CharField(max_length=250, help_text="Title of your topic.")
    module      = models.SlugField(max_length=250, unique=True, help_text="Module to use to create your topic.")
    slug        = models.SlugField(max_length=250, unique=True, help_text="Token to use into the url.")
    description = models.TextField(null=True, blank=True, help_text="A short description of what your topic.")
    public      = models.BooleanField(help_text="Is your topic public?", default=True)
    ontology    = models.FileField(null=True, blank=True, upload_to="ontologies", help_text="Ontology file that descibes your field of study.")

    def __unicode__(self):
        return self.title

    def clean(self):
        if self.ontology == "" and not self.has_default_ontology():
            raise ValidationError( 'An ontology file is required with this module.',  code='invalid')
        models.Model.clean(self)


    def save(self):
        from app.detective.register import init_topics
        models.Model.save(self)
        init_topics()

    def has_default_ontology(self):
        module = importlib.import_module("app.detective.topics.%s" % self.module)
        # File if it's a virtual module
        if not hasattr(module, "__file__"): return False
        directory     = os.path.dirname(os.path.realpath( module.__file__ ))
        # Path to the ontology file
        ontology = "%s/ontology.owl" % directory
        return os.path.exists(ontology)


    def get_absolute_path(self):
        return "/%s/" % self.slug

    def link(self):
        path = self.get_absolute_path()
        return '<a href="%s">%s</a>' % (path, path, )
    link.allow_tags = True