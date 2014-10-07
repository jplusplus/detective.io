from neo4django.db import connection
import re

def by_name(terms, app_label):
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
    """ % (app_label)

    return connection.cypher(query).to_dicts()