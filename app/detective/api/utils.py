from django.conf.urls.defaults import *
from django.forms.forms        import pretty_name
from forms                     import register_model_rules
from neo4django.db             import connection
from random                    import randint


def get_model_fields(model):
    fields      = []
    modelsRules = register_model_rules().model(model)
    if hasattr(model, "_meta"):          
        # Create field object
        for fieldRules in modelsRules.fields():
            f = model._meta.get_field(fieldRules.name)
            # Ignores field terminating by + or begining by _
            if not f.name.endswith("+") and not f.name.endswith("_set") and not f.name.startswith("_"):             
                # Find related model for relation
                if hasattr(f, "target_model"):                            
                    target_model  = f.target_model                     
                    related_model = target_model.__name__
                else:
                    related_model = None     
                
                field = {
                    'name'         : f.name,
                    'type'         : f.get_internal_type(),
                    'help_text'    : getattr(f, "help_text", ""),
                    'verbose_name' : getattr(f, "verbose_name", pretty_name(f.name)),
                    'related_model': related_model,
                    'rules'        : fieldRules.all()
                }
                
                fields.append(field)

    return fields

def get_model_nodes():
    # Return buffer values
    if hasattr(get_model_nodes, "buffer"): 
        results = get_model_nodes.buffer
        # Refresh the buffer ~ 1/10 calls
        if randint(0,10) == 10: del get_model_nodes.buffer
        return results
    query = """
        START n=node(*)
        MATCH n-[r:`<<TYPE>>`]->t
        WHERE HAS(t.name)
        RETURN t.name as name, ID(t) as id
    """
    # Bufferize the result
    get_model_nodes.buffer = connection.cypher(query).to_dicts()    
    return get_model_nodes.buffer
    

def get_model_node_id(model):
    # All node from neo4j that are have ascending <<TYPE>> relationship
    nodes = get_model_nodes()
    try:
        # Search for the node with the good name
        model_node  = next(n for n in nodes if n["name"] == "detective:%s" % model.__name__)
        return model_node["id"] or None
    # We didn't found the node id
    except StopIteration:
        return None