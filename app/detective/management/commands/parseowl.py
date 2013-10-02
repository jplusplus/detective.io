# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from lxml import etree
from app.detective.utils import to_class_name, to_camelcase, to_underscores
import re

# Defines the owl and rdf namespaces
namespaces = {
    'owl': 'http://www.w3.org/2002/07/owl#', 
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#', 
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#'
}
# transform property name
pron = lambda name: to_underscores(to_camelcase(name))

# get local tag
def get(sets, el):
    if hasattr(sets, "iterchildren"):
        props = [ e for e in sets.iterchildren() if re.search('#}%s$' % el, e.tag) ]
        return props[0].text if len(props) else ''
    else:
        return ""

# Merge 2 list and remove duplicates using the given field as reference
def merge(first_list, second_list, field):        
    refs = [ x[field] for x in second_list ]
    return second_list + [ x for x in first_list if x[field] not in refs ]


class Command(BaseCommand):
    help = "Parse the given OWL file to generate its neo4django models."    
    args = 'filename.owl'
    root = None


    def handle(self, *args, **options):
        if not args:
            raise CommandError('Please specify path to ontology file.')            
        
        # Gives the ontology URI. Only needed for documentation purposes
        ontologyURI = "http://www.semanticweb.org/nkb/ontologies/2013/6/impact-investment#"
        # This string will contain the models.py file
        headers = [
            "# -*- coding: utf-8 -*-", 
            "# The ontology can be found in its entirety at %s" % ontologyURI,
            "from neo4django.db import models",
            "from neo4django.auth.models import User",
            ""
        ]


        # This array contains the correspondance between data types
        correspondanceTypes = {
            "string" : "StringProperty",
            "anyURI" : "URLProperty",
            "int" : "IntegerProperty",
            "nonNegativeInteger" : "IntegerProperty",
            "nonPositiveInteger" : "IntegerProperty",
            "PositiveInteger" : "IntegerProperty",
            "NegativeInteger" : "IntegerProperty",
            # Looking forward the neo4django float support!
            # See also: https://github.com/scholrly/neo4django/issues/197
            "float" : "IntegerProperty", 
            "integer" : "IntegerProperty",
            "dateTimeStamp" : "DateTimeProperty",
            "dateTime" : "DateTimeProperty",
            "boolean" : "BooleanProperty"
        }

        try :
            # Parses the file with etree
            tree = etree.parse(args[0])                        
        except:                
            raise CommandError('Unable to parse the given file.')
        
        self.root = tree.getroot()                        
        models = []

        # Finds all the Classes
        for ontologyClassElement in self.root.findall("owl:Class", namespaces):

            # Finds the URI of the class
            classURI = ontologyClassElement.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"]

            #Finds the name of the class
            className = to_class_name(classURI.split("#")[1])

            # By default, the class has no parent
            parentClass = "models.NodeModel"

            # Declares an array to store the relationships and properties from this class
            relations = []
            properties = []


            scope = get(ontologyClassElement, "scope").replace("'", "\\'")
            # Class help text
            help_text = get(ontologyClassElement, "help_text").replace("'", "\\'")
            # Verbose names
            verbose_name = get(ontologyClassElement, "verbose_name").replace("'", "\\'")
            verbose_name_plural = get(ontologyClassElement, "verbose_name_plural").replace("'", "\\'")
            
            # Finds all the subClasses of the Class
            for subClassElement in ontologyClassElement.findall("rdfs:subClassOf", namespaces):
                
                # If the Class is actually an extension of another Class
                if "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource" in subClassElement.attrib:

                    parentClassURI = subClassElement.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"]
                    parentClass = to_class_name(parentClassURI.split("#")[1])

                else:

                    for restriction in subClassElement.findall("owl:Restriction", namespaces):

                        # If there is a relationship defined in the subclass
                        if restriction.find("owl:onClass", namespaces) is not None:

                            # Finds the relationship and its elements 
                            # (destination Class and type)
                            relationClass    = restriction.find("owl:onClass", namespaces) 
                            relation         = {}   
                            relation["URI"]  = relationClass.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"] 
                            relation["name"] = to_class_name(relation["URI"].split("#")[1])

                            # Exception when the relation's destination is 
                            # an individual from the same class
                            if relation["name"] == className:
                                relation["name"] = '"self"'
                            else:
                                relation["name"] = '"%s"' % relation["name"]    


                            relationType     = restriction.find("owl:onProperty", namespaces)
                            relationTypeURI  = relationType.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"]
                            relation["type"] = relationTypeURI.split("#")[1]

                            # Guesses the destination of the relation based on the name. 
                            # Name should be "has_..."
                            if relation["type"].find('has') == 0:
                                relation["destination"] = pron(relation["type"][3:])

                                # Get the property's options
                                options = self.propOptions(relation["type"])                            
                                
                                # Help text
                                relation["help_text"]    = get(options, "help_text").replace("'", "\\'")
                                # Verbose name
                                relation["verbose_name"] = get(options, "verbose_name")                                                                                     
                                relation["type"]         = relation["type"]

                                # Adds the relationship to the array containing all relationships for the class only 
                                # if the relation has a destination              
                                if "destination" in relation:
                                    relations.append(relation)

                        # If there is a property defined in the subclass
                        elif restriction.find("owl:onDataRange", namespaces) is not None or restriction.find("owl:someValuesFrom", namespaces) is not None:
                            propertyTypeElement = restriction.find("owl:onProperty", namespaces)
                            propertyTypeURI     = propertyTypeElement.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"]
                            propertyType        = propertyTypeURI.split("#")[1]

                            if restriction.find("owl:onDataRange", namespaces) is not None:
                                dataTypeElement = restriction.find("owl:onDataRange", namespaces)
                            else:
                                dataTypeElement = restriction.find("owl:someValuesFrom", namespaces)

                            dataTypeURI = dataTypeElement.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"]

                            t = dataTypeURI.split("#")[1]                            

                            if t in correspondanceTypes:
                                dataType = correspondanceTypes[t]
                                # Get the property's options
                                options = self.propOptions(propertyType)

                                prop = {
                                    "name" : propertyType,
                                    "type" : dataType,
                                    # Help text
                                    "help_text": get(options, "help_text").replace("'", "\\'"),
                                    # Verbose name
                                    "verbose_name": get(options, "verbose_name")
                                }

                                properties.append(prop)     
                            else:
                                raise CommandError("Property '%s' of '%s' using unkown type: %s" % (propertyType, className, t) )                                

            models.append({
                "className"          : className,
                "scope"              : scope,
                "help_text"          : help_text,
                "verbose_name"       : verbose_name,
                "verbose_name_plural": verbose_name_plural,
                "parentClass"        : parentClass,
                "properties"         : properties,
                "relations"          : relations,
                "dependencies"       : [parentClass]
            })

        # Topological sort of the model to avoid dependance missings
        models = self.topolgical_sort(models)
        # Output the models file
        self.print_models(models, headers)


    # option of the given property
    def propOptions(self, name):
        
        options = None
        attr    = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"

        for p in self.root.findall("owl:ObjectProperty", namespaces):            
            if re.search('#%s$' % name, p.attrib[attr]):                                
                options = p
        for p in self.root.findall("owl:DatatypeProperty", namespaces):            
            if re.search('#%s$' % name, p.attrib[attr]):                                
                options = p

        return options

    @staticmethod
    def print_models(models=[], headers=[]):

        modelsContents = headers

        for m in models:
            # Writes the class in models.py
            modelsContents.append("\nclass "+ m["className"] +"(models.NodeModel):")

            # Defines properties and relations that every model have
            m["relations"].insert(0,
                {
                    "name" : "User",                    
                    "destination": "_author",
                    "type": pron(m["className"]) + "_has_admin_author",
                    # Verbose name
                    "verbose_name": "author",
                    "help_text": "People that edited this entity."  
                }
            )
            m["properties"].insert(0,
                {
                    "name" : "_status",                    
                    "type": "IntegerProperty",
                    # Verbose name
                    "verbose_name": "status",
                    "help_text": ""
                }
            )

            # Since neo4django doesn't support model inheritance correctly
            # we use models.NodeModel for every model
            # and duplicates parent's attributes into its child
            if m["parentClass"] != "models.NodeModel":
                modelsContents.append("\t_parent = u'%s'" % m["parentClass"])
                # Find the models that could be the parent of the current one
                parents = [model for model in models if model["className"] == m["parentClass"] ]                
                # We found at least one parent
                if len(parents):
                    # We take the first one
                    parent = parents[0]
                    # We merge the properties and the relationships
                    m["properties"] = merge(parent["properties"], m["properties"], "name")
                    m["relations"]  = merge(parent["relations"], m["relations"], "destination")


            if m["scope"] != '' and m["scope"] != None:
                modelsContents.append("\t_scope = u'%s'" % m["scope"])

            if m["help_text"] != None:
                modelsContents.append("\t_description = u'%s'" % m["help_text"])
            
            # Writes the properties 
            for prop in m["properties"]:     
                opt = [                 
                    "null=True",
                    "help_text=u'%s'" % prop["help_text"] 
                ]

                if prop["verbose_name"] != '':
                    opt.append("verbose_name=u'%s'" % prop["verbose_name"])

                field = "\t%s = models.%s(%s)"
                opt = ( pron(prop["name"]), prop["type"],  ",".join(opt)) 
                modelsContents.append(field % opt )               

            # Writes the relationships
            for rel in m["relations"]:  

                opt = [                  
                    rel["name"], 
                    "null=True",
                    # Add class name prefix to relation type
                    "rel_type='%s+'" % pron( m["className"] + "_" + rel["type"] ), 
                    "help_text=u'%s'" % rel["help_text"]
                ]

                if prop["verbose_name"] != '':
                    opt.append("verbose_name=u'%s'" % rel["verbose_name"])

                field = "\t%s = models.Relationship(%s)"
                modelsContents.append(field % (rel["destination"], ",".join(opt) ) )                

            modelsContents.append("\n\tclass Meta:")

            if m["verbose_name"] != '':
                modelsContents.append("\t\tverbose_name = u'%s'" % m["verbose_name"])
            if m["verbose_name_plural"] != '':
                modelsContents.append("\t\tverbose_name_plural = u'%s'" % m["verbose_name_plural"])

            if m["verbose_name"] == '' and  m["verbose_name_plural"] == '':
                modelsContents.append("\t\tpass") 

            if len([p for p in m["properties"] if p["name"] == "name" ]):
                modelsContents.append("\n\tdef __unicode__(self):") 
                modelsContents.append("\t\treturn self.name or u\"Unkown\"") 


        print "\n".join(modelsContents).encode("UTF-8")

    @staticmethod
    def topolgical_sort(graph_unsorted):
        """
        :src http://blog.jupo.org/2012/04/06/topological-sorting-acyclic-directed-graphs/
            
        Repeatedly go through all of the nodes in the graph, moving each of
        the nodes that has all its edges resolved, onto a sequence that
        forms our sorted graph. A node has all of its edges resolved and
        can be moved once all the nodes its edges point to, have been moved
        from the unsorted graph onto the sorted one.
        """

        # This is the list we'll return, that stores each node/edges pair
        # in topological order.
        graph_sorted = []

        # Run until the unsorted graph is empty.
        while graph_unsorted:

            # Go through each of the node/edges pairs in the unsorted
            # graph. If a set of edges doesn't contain any nodes that
            # haven't been resolved, that is, that are still in the
            # unsorted graph, remove the pair from the unsorted graph,
            # and append it to the sorted graph. Note here that by using
            # using the items() method for iterating, a copy of the
            # unsorted graph is used, allowing us to modify the unsorted
            # graph as we move through it. We also keep a flag for
            # checking that that graph is acyclic, which is true if any
            # nodes are resolved during each pass through the graph. If
            # not, we need to bail out as the graph therefore can't be
            # sorted.
            acyclic = False
            for index, item in enumerate(graph_unsorted):      
                edges = item["dependencies"]
                
                node_unsorted = [item_unsorted["className"] for item_unsorted in graph_unsorted]

                for edge in edges:
                    if edge in node_unsorted:                                
                        break
                else:
                    acyclic = True
                    del graph_unsorted[index]
                    graph_sorted.append(item)

            if not acyclic:
                # Uh oh, we've passed through all the unsorted nodes and
                # weren't able to resolve any of them, which means there
                # are nodes with cyclic edges that will never be resolved,
                # so we bail out with an error.
                raise RuntimeError("A cyclic dependency occurred")

        return graph_sorted

