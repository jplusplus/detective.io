angular.module('detective.directive').directive "card", ['Summary', 'Individual', '$sce', (Summary, Individual, $sce)->
    restrict: 'E'
    require: "ngModel"
    scope:
        individual: "=ngModel"
        topic     : "="
        username  : "="
        type      : "="
        field     : "="
        parent    : "="
    templateUrl: "/partial/topic.single.card.html"
    replace: true
    link: (scope, elm, attr) ->
        type = scope.type.toLowerCase()
        # Fields of the current model
        scope.properties = []
        # Fields of the model that describes the relationship
        scope.relProperties = []
        # Values of the model that describes the relationship
        scope.relIndividual = {}
        # Link parameters
        scope.singleParams = ->
            username: scope.username
            topic: scope.topic
            type: type
            id: scope.individual.id
        # Get the value for the given field name with the current individual
        scope.get = (name, isrel=no)->
            unless isrel
                scope.individual[name] or false
            else
                scope.relIndividual[name] or false
        scope.getTrusted = (n) ->
            val = scope.get n
            if val? and val.length > 0 then ($sce.trustAsHtml val) else ""
        # True if the given property is a string
        scope.isString = (f)-> ["CharField", "URLField"].indexOf(f.type) > -1
        scope.isRich = (field) -> field.rules.is_rich or no
        # This individual might have visible properties
        scope.mightHaveProperties = -> scope.field.rules.has_properties or scope.model? and not scope.model.rules.is_searchable
        # True if the given type is literal
        isLiteral = (f)-> ["CharField", "DateTimeField", "URLField", "IntegerField", "BooleanField"].indexOf(f.type) > -1
        # Does the given property has a value within the current individual
        hasValue = (f, isrel=no)-> f.name != 'name' and scope.get(f.name, isrel)
        # Display or not the given field
        filterField = (f)-> isLiteral(f) and hasValue(f)
        # Get the form description for the current model
        Summary.cachedGet id:'forms', (forms)->
            # Save only the type of the current individual
            scope.model = forms[type]
            return if not scope.model?
            # A model might be use to describe this relationship
            if scope.field.rules.through?
                scope.relModel = forms[scope.field.rules.through.toLowerCase()]
            # Should we collect properties?
            if scope.mightHaveProperties()
                # Get model properties for the current model
                scope.properties = _.filter scope.model.fields, filterField
        # Load properties
        scope.loadRelProperties = ->
            return if scope.loadingProperties?
            # Do not try to load properties for nothin
            return unless scope.field.rules.has_properties
            # It must have a parent to connect to
            return unless scope.parent?
            # Load properties once
            scope.loadingProperties = yes
            params =
                type  : scope.field.model.toLowerCase()
                id    : scope.parent.id
                field : scope.field.name
                target: scope.individual.id
            # Save the properties
            Individual.relationships params, (individual)->
                scope.relIndividual = individual
                scope.relProperties = _.filter scope.relModel.fields, (f)->
                    # Filter literal values and existing value
                    isLiteral(f) and hasValue(f, yes)
                scope.loadingProperties = no

]