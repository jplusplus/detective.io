from django.core.management.base import BaseCommand, CommandError
from lxml import etree


class Command(BaseCommand):
	help = "Parse the given OWL file to generate its neo4django models."    
	args = 'filename.owl'

	def handle(self, *args, **options):

		if not args:
			raise CommandError('Please specify path to ontology file.')
		

		# This string will contain the models.py file
		modelsContents = "from neo4django.db import models\n\n"
		# Gives the ontology URI. Only needed for documentation purposes
		ontologyURI = "http://www.semanticweb.org/nkb/ontologies/2013/6/impact-investment#"
		# Adds a comment in the models.py file
		modelsContents += "# The ontology can be found in its entirety at " + ontologyURI + "\n"
		# Defines the owl and rdf namespaces
		namespaces = {
			'owl': 'http://www.w3.org/2002/07/owl#', 
			'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#', 
			'rdfs': 'http://www.w3.org/2000/01/rdf-schema#'
		}

		# This array contains the correspondance between data types
		correspondanceTypes = {
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
			"string" : "StringArrayProperty",
			"boolean" : "BooleanProperty"
		}

		try :
			# Parses the file with etree
			tree = etree.parse(args[0])
			root = tree.getroot()
		except:			
			raise CommandError('Unable to parse the given file.')

		# Finds all the Classes
		for ontologyClassElement in root.findall("owl:Class", namespaces):
			# Defines the array that contains the class information
			ontologyClass = {}
			# Finds the URI of the class
			classURI = ontologyClassElement.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"]
			#Finds the name of the class
			className = classURI.split("#")[1]
			# By default, the class has no parent
			parentClass = "models.NodeModel"

			# Declares an array to store the relationships and properties from this class
			relations = []
			properties = []

			# Finds all the subClasses of the Class
			for subClassElement in ontologyClassElement.findall("rdfs:subClassOf", namespaces):

				# If the Class is actually an extension of another Class
				if "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource" in subClassElement.attrib:

					parentClassURI = subClassElement.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"]
					parentClass = parentClassURI.split("#")[1]		

				else:

					for restriction in subClassElement.findall("owl:Restriction", namespaces):

						# If there is a relationship defined in the subclass
						if restriction.find("owl:onClass", namespaces) is not None:

							# Finds the relationship and its elements (destination Class and type)
							relationClass = restriction.find("owl:onClass", namespaces)	
							relation = {}	
							relation["URI"] = relationClass.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"]	
							relation["name"] = relation["URI"].split("#")[1]

							# Exception when the relation's destination is an individual from the same class
							if relation["name"] == className:

								relation["name"] = 'self'

							relationType = restriction.find("owl:onProperty", namespaces)
							relationTypeURI = relationType.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"]
							relation["type"] = relationTypeURI.split("#")[1]

							# Guesses the destination of the relation based on the name. Name should be "has..."
							if relation["type"].find('has') == 0:
								relation["destination"] = relation["type"][3:].lower()

							# Adds the relationship to the array containing all relationships for the class only if the relation has a destination				
							if "destination" in relation:
								relations.append(relation)

						# If there is a property defined in the subclass
						elif restriction.find("owl:onDataRange", namespaces) is not None:
							propertyTypeElement = restriction.find("owl:onProperty", namespaces)
							propertyTypeURI = propertyTypeElement.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"]
							propertyType = propertyTypeURI.split("#")[1]
							dataTypeElement = restriction.find("owl:onDataRange", namespaces)
							dataTypeURI = dataTypeElement.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"]
							dataType = correspondanceTypes[dataTypeURI.split("#")[1]]
							
							property_ = {
								"name" : propertyType,
								"type" : dataType
							}

							properties.append(property_)

			# Writes the class in models.py
			modelsContents += "\nclass "+ className +"(" + parentClass + "):\n"

			# Writes the properties	
			for property_ in properties:	
				modelsContents += "\t" + property_["name"] + " = models." + property_["type"] + "()\n"

			# Writes the relationships
			for relationship in relations:	
				modelsContents += "\t" + relation["destination"] + " = models.Relationship(" + relation["name"] + ",rel_type='" + relation["type"] + "')\n"

			if len(properties) == 0 and len(relations) == 0:
				modelsContents += "\tpass"

		print modelsContents

