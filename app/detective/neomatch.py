from neo4django.db    import connection
from django.db.models import get_app, get_models

class Neomatch(object):

    def __init__(self, match, title=""):        
        self.select = "end_obj"
        self.model  = "model_obj"
        # Save the attributes
        self.match  = str(match)
        self.title  = title
        # Build the query
        self.query_str = """
            START root=node({root})
            MATCH {match}
            RETURN {select}, ID({select}) as id, ID({model}) as model_id, {model}.model_name as model_name 
        """
    # Process the query to the database
    def query(self, root="*"):
        # Replace the query's tags 
        # by there choosen value
        query = self.query_str.format(
            root=root, 
            match=self.match.format(
                select=self.select,
                model=self.model
            ),
            select=self.select,
            model=self.model
        )
        # Execute the query and returnt the result as a dictionnary
        return self.transform(connection.cypher(query).to_dicts())
    # Transform neo4j result to a more understable list 
    def transform(self, items):
        results = []
        app     = get_app('detective')
        models  = get_models(app)

        for item in items:
            model = next(m for m in models if m.__name__ == item["model_name"])
            if model:
                # Keep the result only if we know its model
                results.append({
                    'model' : {
                        'id'  : item["model_id"],
                        'name': item["model_name"]
                    },
                    'fields': dict( {'id':item["id"]}.items() + item[self.select]["data"].items() )
                })
        return results

