# -*- coding: utf-8 -*-
from app.detective.utils      import to_class_name, to_underscores, create_node_model
from app.detective.modelrules import ModelRules
from neo4django.db            import models

# Shortcut to get a field or None
gn = lambda clss,field,default=None: clss[field] if field in clss else  default

class VirtualApp:
    modelrules = ModelRules()
    # This object contains the correspondance between data types
    JSONTYPES = {
        "relationship" : "Relationship",
        "string"       : "StringProperty",
        "char"         : "StringProperty",
        "url"          : "URLProperty",
        "int"          : "IntegerProperty",
        "integer"      : "IntegerProperty",
        "intarray"     : "IntArrayProperty",
        "integerarray" : "IntArrayProperty",
        "datetimestamp": "DateTimeProperty",
        "datetime"     : "DateTimeProperty",
        "date"         : "DateTimeProperty",
        "time"         : "DateTimeProperty",
        "boolean"      : "BooleanProperty",
        "bool"         : "BooleanProperty",
        # Looking forward the neo4django float support!
        # See also: https://github.com/scholrly/neo4django/issues/197
        "float"        : "StringProperty"
    }

    def __init__(self, module, app_label, ontology):
        # Add dictionary of pending rules that
        # will be added once the model is created
        self.pending_modelrules = dict()
        # Where record the new models
        self.models    = dict()
        self.module    = module
        self.app_label = app_label if app_label is not None else module.split(".")[-1]
        self.ontology  = ontology
        # We accept list of ontologies OR dict of ontologies
        models = ontology.values() if type(ontology) is dict else ontology
        # List models from the ontology
        for idx, desc in enumerate(models):
            # Generate a model
            model = self.add_model(desc)
            model.__idx__ = idx
        # Add pending rules to created models
        for model_name, model_rules in self.pending_modelrules.iteritems():
            # Rules are always related to a model **class**
            model = self.models[model_name]
            # Get the singleton containing rules for this model
            rules = self.modelrules.model(model)
            # Pending rules are related to a field
            for field_name, field_rules in model_rules .iteritems():
                # Add all rules at the same time
                rules.field(field_name).add(**field_rules)


    # Simple getter
    def get_models(self): return self.models

    def get_field_specials(self, desc):
        props = {}
        # List all special propertie
        for prop in ["verbose_name", "help_text", "related_name", "single", "default"]:
            if prop in desc:
                props[prop] = desc[prop]
        # Return an empty dict by default
        return props

    def add_rule(self, model, field, name, value):
        # This model doesn't exist yet
        if not model in self.pending_modelrules:
            self.pending_modelrules[model] = dict()
        # This field doesn't exist yet
        if not field in self.pending_modelrules[model]:
            self.pending_modelrules[model][field] = dict()
        # Set the new rule to the field
        self.pending_modelrules[model][field][name] = value



    def add_model(self, desc, name=None):
        # Extract the class name
        model_name = gn(desc, "name", name).lower()
        # Format the class name to be PEP compliant
        model_name = to_class_name(model_name)
        # Every class fields are recorded into an objects
        model_fields = {
            # Additional informations
            "_description": gn(desc, "help_text", gn(desc, "description")),
            "_topic"      : gn(desc, "scope"),
            # Default fields
            "_author": models.IntArrayProperty(null=True, help_text=u'People that edited this entity.', verbose_name=u'author'),
            "_status": models.IntegerProperty(null=True, help_text=u'',verbose_name=u'status')
        }
        # Pick some options (Meta class)
        model_options = {}

        for f in ["verbose_name", "verbose_name_plural"]:
            # Extract those option into a separate class
            if f in desc: model_options[f] = desc[f]
        fields = []
        # List all fields
        for idx, field in enumerate(gn(desc, 'fields', [])):
            # Get a field instance and its name
            field_name, field_instance = self.get_model_field(field, model_name)
            # No error
            if None not in [field_name, field_instance]:
                # Record the field
                fields.append(field_name)
                model_fields[field_name] = field_instance

        # Creates a module with the extracted options
        self.models[model_name] = create_node_model(model_name, model_fields,
                                                    app_label=self.app_label,
                                                    options=model_options,
                                                    module=self.module)

        self.models[model_name].__fields_order__ = fields

        # Prevent a bug with select_related when using neo4django and virtual models
        if not hasattr(self.models[model_name]._meta, '_relationships'):
            self.models[model_name]._meta._relationships = {}

        return self.models[model_name]


    def get_model_field(self, desc, model_name):
        # All field's options
        field_opts = dict(null=True)
        # Get the name tag
        field_name = gn(desc, 'name')
        # Convert the name to a python readable format
        field_name = to_underscores(field_name)
        # We didn't found a name
        # @TODO handle that with a custom exception
        if field_name is None: return None, None
        # The field can contains rules
        for name, value in gn(desc, 'rules', dict()).iteritems():
            self.add_rule(model_name, field_name, name, value)
        # Get field's special properties
        field_opts = dict( field_opts.items() + self.get_field_specials(desc).items() )
        if field_name == "name":
            field_opts["indexed"] = True
        # It's a relationship!
        if "related_model" in desc and desc["related_model"] is not None:
            field_opts["target"] = to_class_name(desc["related_model"].lower())
            field_target = to_class_name(field_opts["target"])
            # Remove "has_" from the begining of the name
            if field_name.startswith("has_"): field_name = field_name[4:]
            # Build rel_type using the name and the class name
            field_opts["rel_type"] = "%s_has_%s+"  % ( to_underscores(model_name), field_name)
            field_type = "relationship"

            # Add a related name
            if "related_name" in field_opts and field_opts["related_name"] is not None:
                # Convert related_name to the same format
                related_name = field_opts["related_name"]
                related_name = to_underscores(related_name)
                field_opts["related_name"] = related_name
            else:
                related_name = field_opts["related_name"] = None

            # This relationship can embed properties.
            # Properties are directly bound to the relationship field.
            if "fields" in desc:
                # Fields related to the new model
                composite_fields = gn(desc, 'fields', [])
                # Create a field to reference the relationship ID
                composite_fields.append(dict(
                    type="int",
                    name="_relationship",
                    help_text="The ID of the relationship to describe.",
                    indexed=True,
                    rules=dict(is_editable=False)
                ))
                composite_fields.append(dict(
                    type="intarray",
                    name="_endnodes",
                    help_text="IDs of the relationship's extremities.",
                    indexed=True,
                    rules=dict(is_editable=False)
                ))
                # Name of the new model
                composite_name = "%s %s %s Properties" % (
                    model_name,
                    field_name,
                    field_target
                )
                # Create a Model with the relation
                composite_model = {
                    "name": composite_name,
                    "fields": composite_fields
                }
                # Create the new model!
                model = self.add_model(composite_model)
                # We have to register (for later) a rule that says
                # explicitely that this field has properties
                self.add_rule(model_name, field_name, "has_properties", True)
                self.add_rule(model_name, field_name, "through", model)
                # This relationship is visible in the target model
                if related_name is not None:
                    # Add another rule for the reverse relationship
                    self.add_rule(field_target, related_name, "has_properties", True)
                    self.add_rule(field_target, related_name, "through", model)
                # Add a rules to make this "special" model
                self.modelrules.model(model).add(is_relationship_properties=True,
                                                 relationship_source=model_name,
                                                 relationship_target=field_target,
                                                 is_searchable=False)
        # It's a literal value
        else:
            # Picks one of the two tags type
            field_type = desc["type"].lower()
            # Remove "field" suffix
            if field_type.endswith("field"): field_type = field_type[0:-5]
        # Skip unkown type
        # @TODO raise custom exception
        if not field_type in self.JSONTYPES: return None, None
        # Convert type to neo4django property type
        field_type = self.JSONTYPES[field_type]
        # Add a default value for boolean properties
        if field_type == 'BooleanProperty' and not 'default' in field_opts.keys():
            field_opts['default'] = False
        # Return an instance of the field
        return field_name, getattr(models, field_type)(**field_opts)


def parse(ontology, module='', app_label=None):
    # Return the models generated by a new instance of VirtualApp
    return VirtualApp(module, app_label, ontology).get_models()
