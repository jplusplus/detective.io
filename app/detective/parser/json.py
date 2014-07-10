# -*- coding: utf-8 -*-
from app.detective.utils import to_class_name, to_underscores, create_node_model
from neo4django.db       import models

# Shortcut to get a field or None
gn = lambda clss,field,default=None: clss[field] if field in clss else  default

# This object contains the correspondance between data types
JSONTYPES = {
    "relationship" : "Relationship",
    "string"       : "StringProperty",
    "char"         : "StringProperty",
    "url"          : "URLProperty",
    "int"          : "IntegerProperty",
    "integer"      : "IntegerProperty",
    "datetimestamp": "DateTimeProperty",
    "datetime"     : "DateTimeProperty",
    "date"         : "DateTimeProperty",
    "time"         : "DateTimeProperty",
    "boolean"      : "BooleanProperty",
    # Looking forward the neo4django float support!
    # See also: https://github.com/scholrly/neo4django/issues/197
    "float"        : "StringProperty"
}

def get_field_specials(field):
    props = {}
    # List all special propertie
    for prop in ["verbose_name", "help_text", "related_name"," fields"]:
        if prop in field:
            props[prop] = field[prop]
    # Return an empty dict by default
    return props

def get_model_field(field, model_name):
    # All field's options
    field_opts = dict(null=True)
    # Get the name tag
    field_name = gn(field, 'name')
    # Convert the name to a python readable format
    field_name = to_underscores(field_name)
    # We didn't found a name
    if field_name is None: return None, None
    # Get field's special properties
    field_opts = dict( field_opts.items() + get_field_specials(field).items() )
    # It's a relationship!
    if "related_model" in field and field["related_model"] is not None:
        field_opts["target"] = to_class_name(field["related_model"].lower())
        # Remove "has_" from the begining of the name
        if field_name.startswith("has_"): field_name = field_name[4:]
        # Build rel_type using the name and the class name
        field_opts["rel_type"] = "%s_has_%s+"  % ( to_underscores(model_name), field_name)
        field_type = "relationship"
        # Add a related name
        if "related_name" in field_opts and field_opts["related_name"] is not None:
            # Convert related_name to the same format
            field_opts["related_name"] = to_underscores(field_opts["related_name"])
        # This relationship can embed properties
        if "fields" in field:
            # List all fields
            for rel_field in gn(field, 'fields', []):
                # Get a field instance and its name
                field_name, field_instance = get_model_field(rel_field, field_opts["target"])
                # No error
                if None not in [field_name, field_instance]:
                    # Record the field
                    print field_name, field_instance
    # It's a literal value
    else:
        # Picks one of the two tags type
        field_type = field["type"].lower()
        # Remove "field" suffix
        if field_type.endswith("field"):
            field_type = field_type[0:-5]
    # Skip unkown type
    # @TODO raise custom exception
    if not field_type in JSONTYPES: return None, None
    # Convert type to neo4django property type
    field_type = JSONTYPES[field_type]
    # Return an instance of the field
    return field_name, getattr(models, field_type)(**field_opts)


def get_model(desc, module, app_label):
    # Extract the class name
    model_name = gn(desc, "name").lower()
    # Format the class name to be PEP compliant
    model_name = to_class_name( model_name )
    # Every class fields are recorded into an objects
    model_fields = {
        # Additional informations
        "_description": gn(desc, "help_text", gn(desc, "description")),
        "_topic"      : gn(desc, "scope"),
        # Default fields
        "_author": models.IntArrayProperty(null=True, help_text=u'People that edited this entity.', verbose_name=u'author'),
        "_status": models.IntegerProperty(null=True,help_text=u'',verbose_name=u'status')
    }
    # Pick some options (Meta class)
    class_options = {}

    for f in ["verbose_name", "verbose_name_plural"]:
        # Extract those option into a separate class
        if f in desc: class_options[f] = desc[f]
    # List all fields
    for field in gn(desc, 'fields', []):
        # Get a field instance and its name
        field_name, field_instance = get_model_field(field, model_name)
        # No error
        if None not in [field_name, field_instance]:
            # Record the field
            model_fields[field_name] = field_instance

    return model_name, create_node_model(model_name, model_fields, app_label=app_label, options=class_options, module=module)


def parse(ontology, module='', app_label=None):
    app_label = app_label if app_label is not None else module.split(".")[-1]
    # Where record the new models
    models = dict()
    # List models
    for name in ontology:
        desc = ontology[name]
        # Genere a model
        model_name, model = get_model(desc, module, app_label)
        # Record the class with this fields
        models[model_name] = model
        # Prevent a bug with select_related when using neo4django and virtual models
        if not hasattr(models[model_name]._meta, '_relationships'):
            models[model_name]._meta._relationships = {}
    return models