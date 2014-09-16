import re
from neo4jrestclient   import client
from neo4django.db     import connection
from django.core.cache import cache

# Extract node id from given node uri
def node_id(uri):
    return int( re.search(r'(\d+)$', uri).group(1) )

# Get the end of the given relationship
def rel_from(rel, side):
    return node_id(rel._dic[side])

# Is the given relation connected to the given idx
def connected(rel, idx):
    return rel_from(rel, "end") == idx or rel_from(rel, "start") == idx

# Get the opposite node id according the given relationship
def opposite(rel, idx):
    side = "start" if rel_from(rel, "end") == idx else "end"
    return rel_from(rel, side)

# Get the node for the given model class
def get_model_node(model):
    # Retreive the name of the model in the database
    model_db_name = "%s:%s" % (model._meta.app_label, model.__name__)
    model_cache_key = "model_node_%s" % model_db_name
    # Use the cache?
    if cache.get(model_cache_key, None) is not None: cache.get(model_cache_key)
    # Build the query to retreive this model
    query = """
        START n=node(0)
        MATCH n-[r:`<<TYPE>>`]->m
        WHERE HAS(m.name)
        AND m.name = '%s'
        RETURN m
    """ % model_db_name
    # Extract the node for this model
    model_node = connection.query(query, returns=(client.Node,) )
    # Does the node exist for this model?
    if len(model_node):
        # Cache the node for later
        cache.set(model_cache_key, model_node[0][0])
        # And returns it
        return model_node[0][0]
    # The model may not exist YET
    else:
        # We force neo4django to create the model into the database
        # by creating a node from this model
        node = model()
        node.save()
        # Then we delete it instantanetly
        node.delete()
        # And recursivly call this function
        return get_model_node(model)