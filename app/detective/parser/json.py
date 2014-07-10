# -*- coding: utf-8 -*-
from app.detective.utils import to_class_name, to_underscores, create_node_model
from neo4django.db       import models

# Shortcut to get a field or None
gn = lambda clss,field,default=None: clss[field] if field in clss else  default

class VirtualApp(object):
    # Where record the new models
    models = dict()
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

    def __init__(self, module, app_label, ontology):
        self.module    = module
        self.app_label = app_label
        self.ontology  = ontology
        # List models from the ontology
        for name in ontology:
            # Each model has its own descriptor
            desc = ontology[name]
            # Genere a model
            self.add_model(desc)

    # Simple getter
    def get_models(self): return self.models

    def get_field_specials(self, desc):
        props = {}
        # List all special propertie
        for prop in ["verbose_name", "help_text", "related_name"]:
            if prop in desc:
                props[prop] = desc[prop]
        # Return an empty dict by default
        return props

    def add_model(self, desc):
        # Extract the class name
        model_name = gn(desc, "name").lower()
        # Format the class name to be PEP compliant
        model_name = to_class_name(model_name)
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
        model_options = {}

        for f in ["verbose_name", "verbose_name_plural"]:
            # Extract those option into a separate class
            if f in desc: model_options[f] = desc[f]
        # List all fields
        for field in gn(desc, 'fields', []):
            # Get a field instance and its name
            field_name, field_instance = self.get_model_field(field, model_name)
            # No error
            if None not in [field_name, field_instance]:
                # Record the field
                model_fields[field_name] = field_instance

        # Creates a module with the extracted options
        self.models[model_name] = create_node_model(model_name, model_fields,
                                                    app_label=self.app_label,
                                                    options=model_options,
                                                    module=self.module)

        return self.models[model_name]


    def get_model_field(self, desc, model_name):
        # All field's options
        field_opts = dict(null=True)
        # Get the name tag
        field_name = gn(desc, 'name')
        # Convert the name to a python readable format
        field_name = to_underscores(field_name)
        # We didn't found a name
        if field_name is None: return None, None
        # Get field's special properties
        field_opts = dict( field_opts.items() + self.get_field_specials(desc).items() )
        # It's a relationship!
        if "related_model" in desc and desc["related_model"] is not None:
            field_opts["target"] = to_class_name(desc["related_model"].lower())
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
            if "fields" in desc:
                # List all fields
                for rel_field in gn(desc, 'fields', []):
                    # Get a field instance and its name
                    field_name, field_instance = self.get_model_field(rel_field, field_opts["target"])
                    # No error
                    if None not in [field_name, field_instance]:
                        # Record the field
                        print field_name, field_instance
        # It's a literal value
        else:
            # Picks one of the two tags type
            field_type = desc["type"].lower()
            # Remove "field" suffix
            if field_type.endswith("field"):
                field_type = field_type[0:-5]
        # Skip unkown type
        # @TODO raise custom exception
        if not field_type in self.JSONTYPES: return None, None
        # Convert type to neo4django property type
        field_type = self.JSONTYPES[field_type]
        # Return an instance of the field
        return field_name, getattr(models, field_type)(**field_opts)


def parse(ontology, module='', app_label=None):
    app_label = app_label if app_label is not None else module.split(".")[-1]
    # Return the models generated by a new instance of VirtualApp
    return VirtualApp(module, app_label, ontology).get_models()