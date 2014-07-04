# -*- coding: utf-8 -*-
from app.detective.utils import to_class_name, to_underscores, create_node_model
from neo4django.db       import models

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
    for prop in ["verbose_name", "help_text", "related_name"]:
        if prop in field:
            props[prop] = field[prop]
    # Return an empty dict by default
    return props

def parse(ontology, module='', app_label=None):
    app_label = app_label if app_label is not None else module.split(".")[-1]
    # Shortcut to get a field or None
    gn = lambda clss,field,default=None: clss[field] if field in clss else  default
    # Where record the new classes
    classes = dict()
    # List classes
    for name in ontology:
        clss = ontology[name]
        # Extract the class name
        class_name = gn(clss, "name", name).lower()
        # Format the class name to be PEP compliant
        class_name = to_class_name( class_name )
        # Every class fields are recorded into an objects
        class_fields = {
            # Additional informations
            "_description": gn(clss, "help_text"),
            "_topic"      : gn(clss, "scope"),
            # Default fields
            "_author": models.IntArrayProperty(null=True, help_text=u'People that edited this entity.', verbose_name=u'author'),
            "_status": models.IntegerProperty(null=True,help_text=u'',verbose_name=u'status')
        }
        # Pick some options (Meta class)
        class_options = {}

        for f in ["verbose_name", "verbose_name_plural"]:
            # Extract those option into a separate class
            if f in clss: class_options[f] = clss[f]
        # List all fields
        for field in gn(clss, 'fields', []):
            # All field's options
            field_opts = dict(null=True)
            # Get the name tag
            field_name = gn(field, 'name')
            # Convert the name to a python readable format
            field_name = to_underscores(field_name)
            # We didn't found a name
            if field_name is None: continue
            # Get field's special properties
            field_opts = dict( field_opts.items() + get_field_specials(field).items() )
            # It's a relationship!
            if "related_model" in field and field["related_model"] is not None:
                field_opts["target"] = to_class_name(field["related_model"].lower())
                # Remove "has_" from the begining of the name
                if field_name.startswith("has_"): field_name = field_name[4:]
                # Build rel_type using the name and the class name
                field_opts["rel_type"] = "%s_has_%s+"  % ( to_underscores(class_name), field_name)
                field_type = "relationship"
                # Add a related name
                if "related_name" in field_opts and field_opts["related_name"] is not None:
                    # Convert related_name to the same format
                    field_opts["related_name"] = to_underscores(field_opts["related_name"])
            else:
                # Picks one of the two tags type
                field_type = field["type"].lower()
                # Remove "field" suffix
                if field_type.endswith("field"):
                    field_type = field_type[0:-5]
            # Skip unkown type
            # @TODO raise custom exception
            if not field_type in JSONTYPES: continue
            # Convert type to neo4django property type
            field_type = JSONTYPES[field_type]
            # Record the field
            class_fields[field_name] = getattr(models, field_type)(**field_opts)
        # Record the class with this fields
        classes[class_name] = create_node_model(class_name, class_fields, app_label=app_label, options=class_options, module=module)
        # Prevent a bug with select_related when using neo4django and virtual models
        if not hasattr(classes[class_name]._meta, '_relationships'):
            classes[class_name]._meta._relationships = {}
    return classes