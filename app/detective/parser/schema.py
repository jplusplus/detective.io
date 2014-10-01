from jsonschema import FormatChecker
from jsonschema.exceptions import ValidationError
import copy


def is_modelname(ontology):
	names = [ model["name"] for model in ontology ]
	def ontology_has_name(name):
		return name in names
	return ontology_has_name

def checker(ontology):
	modelname_checker = FormatChecker()
	# Pass the ontology object as a closure
	modelname_checker.checks("modelname", raises=ValidationError)(is_modelname(ontology))
	# Returns the checker after configuring it
	return modelname_checker


# Field validation schema
field = {
	"type": "object",
	"properties": {
		"name": {
			"type": "string"
		},
		"type": {
			"type": "string",
			"enum": [
				"float",
				"relationship",
				"string",
				"char",
				"url",
				"int",
				"integer",
				"intarray",
				"integerarray",
				"datetimestamp",
				"datetime",
				"date",
				"time",
				"boolean",
				"bool"
			]
		},
		"help_text": {
			"type": "string"
		},
		"indexed": {
			"type": "boolean"
		},
		"verbose_name": {
			"type": "string"
		},
		"related_model": {
			"type": "string",
			"format": "modelname"
		},
		"related_name": {
			"type": "string"
		},
		"fields": {
			"type": "array"
		}
	},
	"rules": {
		"type": "object",
		"properties": {
			"is_editable": {
				"type": "boolean"
			},
			"is_searchable": {
				"type": "boolean"
			},
			"is_visible": {
				"type": "boolean"
			},
			"has_properties": {
				"type": "boolean"
			},
			"is_rich": {
				"type": "boolean"
			},
			"through": {
				"type": "modelname"
			},
			"search_terms": {
				"type": ["string", "array"]
			}
		}
	},
	"required": ["name", "type"]
}

# Create an intermetidate object to avoid infinite recurtion
relationship_fields = copy.deepcopy(field)
del relationship_fields["properties"]["fields"]
# Add field itself to the field property
field["properties"]["fields"]["items"] = relationship_fields

# Model validation schema
# Has a nested validation schema for fields.
model = {
	"type": "object",
	"properties": {
		"name": {
			"type": "string"
		},
		"fields": {
			"type": "array",
			"items": field
		},
		"rules": {
			"type": "array"
		},
		"description": {
			"type": "string"
		},
		"help_text": {
			"type": "string"
		},
		"verbose_name": {
			"type": "string"
		},
		"verbose_name_plural": {
			"type": "string"
		},
		"rules": {
			"type": "object",
			"properties": {
				"is_editable": {
					"type": "boolean"
				},
				"is_searchable": {
					"type": "boolean"
				},
				"is_visible": {
					"type": "boolean"
				}
			}
		}
	},
	"required": ["name", "fields"]
}

# Ontology validation schema.
# Has a nested validation schema for models.
ontology = {
	"type" : "array",
	"items": model
}