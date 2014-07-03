# -*- coding: utf-8 -*-
from app.detective.utils           import to_class_name, to_underscores, create_node_model
from django.db.models.fields.files import FieldFile
from lxml                          import etree as ET
from unidecode                     import unidecode
from neo4django.db                 import models

NAMESPACES = {
    'owl': 'http://www.w3.org/2002/07/owl#',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#'
}

# This object contains the correspondance between data types
OWLTYPES = {
    "string" : "StringProperty",
    "anyURI" : "URLProperty",
    "int" : "IntegerProperty",
    "nonNegativeInteger" : "IntegerProperty",
    "nonPositiveInteger" : "IntegerProperty",
    "PositiveInteger" : "IntegerProperty",
    "NegativeInteger" : "IntegerProperty",
    "integer" : "IntegerProperty",
    "dateTimeStamp" : "DateTimeProperty",
    "dateTime" : "DateTimeProperty",
    "boolean" : "BooleanProperty",
    # Looking forward the neo4django float support!
    # See also: https://github.com/scholrly/neo4django/issues/197
    "float" : "StringProperty"
}


def attr(obj, name, default=None):
    tokens = name.split(":")
    if not len(tokens):
        return obj.get(name, default)
    else:
        return obj.get("{%s}%s" % ( NAMESPACES[tokens[0]], tokens[1]), default)

def get_field_specials(root, field_name):
    specials = ["verbose_name", "help_text", "related_name"]
    props = {}
    tags  = root.findall("owl:ObjectProperty",   namespaces=NAMESPACES)
    tags += root.findall("owl:DatatypeProperty", namespaces=NAMESPACES)
    # List all special propertie
    for prop in tags:
        if attr(prop, "rdf:about", "") == field_name:
            # Get the first element txt or the default value
            first = lambda a, d=None: a[0].text if len(a) else d
            for s in specials:
                props[s] = first( prop.xpath("./*[local-name() = '%s']" % s) )
                # Normalize related_name
                if props[s] is not None and s == "related_name":
                    props[s] = unidecode(props[s])

    # Return an empty dict by default
    return props

def get_class_specials(element):
    specials = ["verbose_name", "verbose_name_plural", "help_text", "scope"]
    props = {}
    # Get the first element txt or the default value
    first = lambda a, d=None: a[0].text if len(a) else d
    for s in specials:
        props[s] = first( element.xpath("./*[local-name() = '%s']" % s) )
    # Return an empty dict by default
    return props

def parse(ontology, module='', app_label=None):
    app_label = app_label if app_label is not None else module.split(".")[-1]
    # Deduce the path to the ontology
    if type(ontology) is FieldFile:
        raw = ontology.read()
        # Open the ontology file and returns the root
        root = ET.fromstring(raw)
    else:
        tree = ET.parse(str(ontology))
        # Get the root of the xml
        root = tree.getroot()
    # Where record the new classes
    classes = dict()
    # List classes
    for clss in root.findall("owl:Class", namespaces=NAMESPACES):
        # Extract the class name
        class_name = attr(clss, "rdf:about", "").split('#')[-1]
        # Format the class name to be PEP compliant
        class_name = to_class_name(class_name)
        # Get all special attributes for this class
        class_specials = get_class_specials(clss)
        # Every class fields are recorded into an objects
        class_fields = {
            # Additional informations
            "_description": class_specials["help_text"],
            "_topic"      : class_specials["scope"],
            # Default fields
            "_author": models.IntArrayProperty(null=True, help_text=u'People that edited this entity.', verbose_name=u'author'),
            "_status": models.IntegerProperty(null=True,help_text=u'',verbose_name=u'status')
        }
        # Pick some options (Meta class)
        class_options = {}
        for f in ["verbose_name", "verbose_name_plural"]:
            if class_specials[f] is not None:
                class_options[f] = class_specials[f]
        # List all fields
        for field in clss.findall("rdfs:subClassOf//owl:Restriction", namespaces=NAMESPACES):
            # All field's options
            field_opts = dict(null=True)
            # Get the name tag
            field_name = field.find("owl:onProperty", namespaces=NAMESPACES)
            # We didn't found a name
            if field_name is None: continue
            # Get the complete field name using the rdf:resource attribute
            field_name = attr(field_name, "rdf:resource");
            # Get field's special properties
            field_opts = dict(field_opts.items() + get_field_specials(root, field_name).items() )
            # Convert the name to a python readable format
            field_name = to_underscores(field_name.split("#")[-1])
            if "related_name" in field_opts and field_opts["related_name"] is not None:
                # Convert related_name to the same format
                field_opts["related_name"] = to_underscores(field_opts["related_name"])
            # It might be a relationship
            on_class = field.find("owl:onClass", namespaces=NAMESPACES)
            # It's a relationship!
            if on_class is not None:
                field_opts["target"] = to_class_name(attr(on_class, "rdf:resource").split("#")[-1])
                # Remove "has_" from the begining of the name
                if field_name.startswith("has_"): field_name = field_name[4:]
                # Build rel_type using the name and the class name
                field_opts["rel_type"] = "%s_has_%s+"  % ( to_underscores(class_name), field_name)
                field_type = "Relationship"
            else:
                # Get the type tag
                data_range = field.find("owl:onDataRange", namespaces=NAMESPACES)
                # It might be another tag
                values_from = field.find("owl:someValuesFrom", namespaces=NAMESPACES)
                # Picks one of the two tags type
                field_type = data_range if data_range is not None else values_from
                # It might be nothing!
                if field_type is None: continue
                # Convert the type to a python readable format
                field_type = OWLTYPES[attr(field_type, "rdf:resource").split("#")[-1]]
            # Record the field
            class_fields[field_name] = getattr(models, field_type)(**field_opts)
        # Record the class with this fields
        classes[class_name] = create_node_model(class_name, class_fields, app_label=app_label, options=class_options, module=module)
        # Prevent a bug with select_related when using neo4django and virtual models
        if not hasattr(classes[class_name]._meta, '_relationships'):
            classes[class_name]._meta._relationships = {}
    return classes