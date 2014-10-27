from neo4django.db        import connection
from app.detective.models import SearchTerm
from difflib              import SequenceMatcher
import re

class Search(object):

    def __init__(self, topic):
        self.topic = topic

    def by_name(self, terms):
        if type(terms) in [str, unicode]:
            terms = [terms]
        matches = []
        for term in terms:
            term = unicode(term).lower()
            term = re.sub("\"|'|`|;|:|{|}|\|(|\|)|\|", '', term).strip()
            matches.append("LOWER(node.name) =~ '.*(%s).*'" % term)
        # Query to get every result
        query = """
            START root=node(0)
            MATCH (node)<-[r:`<<INSTANCE>>`]-(type)<-[`<<TYPE>>`]-(root)
            WHERE HAS(node.name) """
        if matches:
            query += """
            AND (%s) """ % ( " OR ".join(matches))
        query += """
            AND type.app_label = '%s'
            RETURN ID(node) as id, node.name as name, type.model_name as model
        """ % (self.topic.app_label())

        return connection.cypher(query).to_dicts()


    def find_matches(self, query):
        # Group ngram by following string
        ngrams  = [' '.join(x) for x in self.ngrams(query) ]
        matches = []
        models  = self.get_syntax().get("subject").get("model")
        rels    = self.get_syntax().get("predicate").get("relationship")
        lits    = self.get_syntax().get("predicate").get("literal")
        # Known models lookup for each ngram
        for token in ngrams:
            obj = {
                'models'       : self.get_close_labels(token, models),
                'relationships': self.get_close_labels(token, rels),
                'literals'     : self.get_close_labels(token, lits),
                'token'        : token
            }
            matches.append(obj)
        return matches

    def build_propositions(self, matches, query):
        """
            For now, a proposition follow the form
            <subject> <predicat> <object>
            Where a <subject>, is a "Named entity" or a Model
            a <predicat> is a relationship type
            and an <object> is a "Named entity" or a Model.
            Later, as follow RDF standard, an <object> could be any data.
        """
        predicates   = []
        subjects     = []
        objects      = []
        propositions = []
        to_search    = set()
        # Picks candidates for subjects and predicates
        for idx, match in enumerate(matches):
            subjects     += match["models"]
            predicates   += match["relationships"] + match["literals"]
            token         = match["token"]
            # Objects are detected when they start and end by double quotes
            if token.startswith('"') and token.endswith('"'):
                # Remove the quote from the token
                token = token.replace('"', '')
                # We may search this term
                to_search.add(token)
            # Or if the previous word is a preposition
            elif self.is_object(match, query, token):
                if token not in to_search and len(token) > 2:
                    # We may search this term
                    to_search.add(token)

        # There is node to look for
        if len(to_search):
            # Search all terms at once
            objects += self.by_name(to_search)
        # Only keep predicates that concern our subjects
        subject_names = set([subject['name'] for subject in subjects])
        predicates = filter(lambda predicate: predicate['subject'] in subject_names, predicates)

        # We find some subjects
        if len(subjects) and not len(predicates):
            terms  = self.get_syntax().get("predicate").get("relationship")
            terms += self.get_syntax().get("predicate").get("literal")
            for subject in subjects:
                # Gets all available terms for these subjects
                predicates += [ term for term in terms if term["subject"] == subject["name"] ]

        # Object related to a given field (field name as key)
        rel_objects = {}
        # Add a default and irrelevant object
        if not len(objects):
            objects = [""]
            fields = set([ (p["name"], p["subject"], getattr(p, "relevance", 0) ) for p in predicates ])
            fields = sorted(fields, key=lambda r: -r[2])
            for f in fields:
                # Extract option
                field_name, model_name, relevance = f
                # Find the model
                model = getattr(self.topic.get_models_module(), model_name, None)
                # No model found
                if model is None: break
                # Find the field
                field = getattr(model, field_name, None)
                # No field found
                if field is None: break
                # Find related model
                rel_objects[field_name] = self.get_most_related(field.rel_type)
                # Stop at the first iteration
                break

        # Generate proposition using RDF's parts
        for subject in self.remove_duplicates(subjects):
            for predicate in self.remove_duplicates(predicates):
                # Merge all object and the objects associated to that field
                field_objects = objects + rel_objects.get(predicate["name"], [])
                for obj in self.remove_duplicates(field_objects):
                    pred_sub = predicate.get("subject", None)
                    # If the predicate has a subject
                    # and it matches to the current one
                    if pred_sub != None and pred_sub == subject.get("name", None):
                        # Target Model of the predicate
                        target = SearchTerm(
                            subject=pred_sub,
                            name=predicate["name"],
                            topic=self.topic
                        ).target

                        if type(obj) is dict:
                            obj_disp = obj["name"] or obj["label"]
                            # Pass this predicate if this object doesn't match
                            # with the current predicate's target
                            if target != obj["model"]: continue
                        else:
                            obj_disp = obj
                        # Value to inset into the proposition's label
                        values = (subject["label"], predicate["label"], obj_disp,)
                        # Build the label
                        label = '%s that %s %s' % values
                        propositions.append({
                            'label'    : label,
                            'subject'  : subject,
                            'predicate': predicate,
                            'object'   : obj
                        })

        # It might be a classic search
        for obj in [ obj for obj in self.remove_duplicates(objects) if 'id' in obj ]:
            # Build the label
            label = obj.get("name", None)
            propositions.append({
                'label': label,
                'subject': {
                    "name": obj.get("id", None),
                    "label": label
                },
                'predicate': {
                    "label": "is instance of",
                    "name": "<<INSTANCE>>"
                },
                'object': obj.get("model", None)
            })
        # Sort propositions by relevance
        propositions = sorted(propositions, key=self.get_proposition_accurancy)
        # Remove duplicates proposition dicts
        return propositions

    @staticmethod
    def get_proposition_accurancy(prop):
        count = prop["object"].get("cnt", 0) if type(prop["object"]) is dict else 0
        relevance = prop["predicate"].get("relevance", 0)
        return -(count + relevance)

    def get_syntax(self):
        if not hasattr(self, "syntax"):
            syntax = self.topic.get_syntax()
            self.syntax = syntax
        return self.syntax

    def get_most_related(self, rel):
        query = """
            START root=node(0)
            MATCH target-[r:`%s`]->(edge)<-[`<<INSTANCE>>`]-(type)<-[`<<TYPE>>`]-(root)
            WHERE type.app_label = "%s"
            AND HAS(edge.name)
            RETURN COUNT(target) as cnt, ID(edge) as id, edge.name as name, type.model_name as model
            ORDER BY cnt DESC
            LIMIT 5
        """ % ( rel, self.topic.app_label() )

        return connection.cypher(query).to_dicts()

    @staticmethod
    def ngrams(input):
        input = input.split(' ')
        output = []
        end = len(input)
        for n in range(1, end+1):
            for i in range(len(input)-n+1):
                output.append(input[i:i+n])
        return output

    @staticmethod
    def remove_duplicates(lst):
        seen = set()
        new_list = []
        for item in lst:
            if type(item) is dict:
                # Create a hash of the dictionary
                obj = hash(frozenset(item.items()))
            else:
                obj = hash(item)
            if obj not in seen:
                seen.add(obj)
                new_list.append(item)
        return new_list

    @staticmethod
    def is_preposition(token=""):
        return unicode(token).lower() in ["aboard", "about", "above", "across", "after", "against",
        "along", "amid", "among", "anti", "around", "as", "at", "before", "behind", "below",
        "beneath", "beside", "besides", "between", "beyond", "but", "by", "concerning",
        "considering",  "despite", "down", "during", "except", "excepting", "excluding",
        "following", "for", "from", "in", "inside", "into", "like", "minus", "near", "of",
        "off", "on", "onto", "opposite", "outside", "over", "past", "per", "plus", "regarding",
        "round", "save", "since", "than", "through", "to", "toward", "towards", "under",
        "underneath", "unlike", "until", "up", "upon", "versus", "via", "with", "within", "without"]

    @staticmethod
    def previous_word(sentence="", base=""):
        if base == "" or sentence == "": return ""
        parts = sentence.split(base)
        return parts[0].strip().split(" ")[-1] if len(parts) else None

    @staticmethod
    def is_object(match, query, token):
        previous = Search.previous_word(query, token)
        return Search.is_preposition(previous) or previous.isdigit() or token.isnumeric() or token == query

    @staticmethod
    def get_close_labels(token, lst, ratio=0.6):
        """
            Look for the given token into the list using labels
        """
        matches = []
        for item in lst:
            cpr = item["label"]
            relevance = SequenceMatcher(None, token, cpr).ratio()
            if relevance >= ratio:
                item["relevance"] = relevance
                matches.append(item)
        return matches