class window.EditTopicBatchCtrl
    @$inject: ['$scope', 'Page', '$rootScope', 'TopicsFactory', '$modal', '$stateParams']
    constructor: (@scope, @Page, @rootScope,  @TopicsFactory, @modal, @stateParams)->
        # Parse the given CSV using header
        @csv = Papa.parse @stateParams.csv, header: yes, dynamicTyping: yes, skipEmptyLines: yes
        @scope.csv = @csv
        # Guess models without user pick
        @scope.models = @getModels @csv
        @scope.models = @populateModels @scope.models, @csv
        @modelsToGraphviz @scope.models
        # Extract picked model from this selection
        @scope.areModels = _.reduce @scope.models, (result, model)->
            result[model.name] = yes
            result
        , {}
        # When the selection changes,
        # we have to guess again what the structure could be
        @scope.$watch "areModels", (userPick)=>
            # We pass the user pick to influence the statistic selection
            @scope.models = @getModels @csv, userPick
            @scope.models = @populateModels @scope.models, @csv
        # Watch for value changes
        , yes

    getModels: (csv, force={})=>
        # Collects stat for every field
        stats = @getFieldsStats csv
        # Fields reconized as models
        models = []
        properties = []
        # Analyse every field
        for field in csv.meta.fields
            if field isnt ''
                # The given field may be a model
                if force[field] or not force[field]? and @mayBeModel field, stats, csv
                    # Add the field to the models list
                    models.push
                        name: field
                        properties: []
                        entities: []
                        names: {}
                else
                    properties.push field
        # If we detect at least one model,
        # imports every remaining properties into the first model
        models[0].properties = properties if models.length
        models

    populateModels: (models, csv)=>
        # Then we collect data for each model
        for model in models
            # Every model must be connected together by default
            for target in models
                # Avoid self-directed relationship
                if model.name isnt target.name
                    model.properties = model.properties.concat target.name
            # Collect model's node
            for row in csv.data
                # Pick properties for this model
                entity = _.pick row, model.properties
                # Use the current model field as name
                entity.name = row[model.name]
                # Convert relationships field to array
                for field, relationships of entity
                    # Find the target model for this field (if there is one)
                    target_model = _.findWhere models, name: field
                    # The field is a relationship
                    entity[field] = [relationships] if target_model?
                # Get the index of entities with the same name
                pk = model.names[ entity.name ]
                # This entity may already exists
                if pk?
                    idx = pk.split(':')[1]
                    # We merge its relationships
                    for field, value of model.entities[idx]
                        # Relationships fields are array
                        if _.findWhere(models, name: field)
                            # Merge array of relationships
                            model.entities[idx][field] = model.entities[idx][field].concat entity[field]
                # Create a hashmap of entities name
                else
                    entity.id = model.name + ":" + model.entities.length
                    # Save its index
                    model.names[entity.name] = entity.id
                    # Save the entity
                    model.entities.push entity
        # Relationships must now
        # be converted to array of index
        for model in models
            # Model's entities
            for entity in model.entities
                # Entitie's fields
                for field, relationships of entity
                    # Find the target model for this field (if there is one)
                    target_model = _.findWhere models, name: field
                    # The field is a relationship
                    if target_model?
                        # Convert its values to an array of index
                        for rel, idx in relationships
                            entity[field][idx] = target_model.names[rel]
        models

    modelsToGraphviz:(models)=>
        console.log models

    # Reconizes if a field is a model using the csv's statistics
    mayBeModel: (field, stats, csv)=>
        count = csv.data.length
        # Is mostly using string
        mostlyString = stats[field].numericValues/count < 0.2
        # Does not contain any empty value
        hasntEmpty = not stats[field].emptyValues
        # Is mostly value, NOT link
        mostlyValue = stats[field].httpValues/count < 0.2
        # Every condition have to be true
        mostlyString and hasntEmpty and mostlyValue

    # Fetch the CSV rows to extract per-field statistic
    getFieldsStats: (csv)=>
        # Prepare an object where every field is an attribute
        # that describes the statitis for this field
        stats = _.reduce csv.meta.fields, (result, field)->
            result[field] =
                numericValues: 0
                emptyValues  : 0
                httpValues   : 0
            result
        , {}
        # Fetch the csv value to make some statistics
        for row in @csv.data
            for field, value of row
                # test for empty value
                if value and value isnt ''
                    # Test for numeric value
                    stats[field].numericValues += not isNaN value
                    # test for http value
                    stats[field].httpValues += ('' + value).indexOf('http') is 0
                else
                    # Count emtpy values too
                    stats[field].emptyValues += 1
        # Returns stats object
        stats



angular.module('detective').controller 'editTopicBatchCtrl', EditTopicBatchCtrl
# EOF
