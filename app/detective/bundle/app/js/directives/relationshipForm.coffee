angular.module('detective.directive').directive "relationshipForm", ()->
    restrict: "A"
    templateUrl: "/partial/topic.form.customize-ontology.relationship-form.html"
    scope:
        models: "="
        relationshipForm: "="
        changeBounds: "="
        submit: "&"
        cancel: "&"
    controller: [ '$scope', ($scope)->
        FIELD_TYPES = ['string', 'float', 'date', 'url']
        # Transform the given string into a valid field name
        toFieldName = (verbose_name)-> getSlug verbose_name, separator: '_'
        # Sanitize the model to make it ready to be inserted
        $scope.sanitizeRelationship = (remove_empty_field=no, populate_empty=no)->
            if $scope.relationship.verbose_name?
                # Generate model name
                $scope.relationship.name = toFieldName $scope.relationship.verbose_name
            # Complete missing data
            $scope.relationship.fields      or= []
            $scope.relationship.type          = "relationship"
            $scope.relationship.rules         = search_terms: []
            $scope.relationship.help_text     = ""
            if $scope.changeBounds
                $scope.relationship.related_model = ($scope.target or name: null).name
                $scope.relationship.model         = ($scope.source or name: null).name
            # Add field array
            $scope.relationship.fields or= []
            # Process each field
            for field, index in $scope.relationship.fields
                # Field name exists?
                unless field.name? or field.name isnt ''
                    # Should we remove empty field?
                    if remove_empty_field
                        delete $scope.relationship.fields[index]
                        $scope.relationship.fields.splice index, 1
                    continue
                # Skip unallowed types
                continue unless $scope.isAllowedType(field)
                # Use name as default verbose name
                field.verbose_name = field.verbose_name or field.name if populate_empty
                # Generate fields name
                field.name = toFieldName field.verbose_name
                # Lowercase first letter
                if field.name.length < 2
                    field.name = do field.name.toLowerCase
                else
                    field.name = field.name.substring(0, 1).toLowerCase() + field.name.substring(1)
            # Remove empty field if needed
            delete $scope.relationship.fields if $scope.relationship.fields.length is 0 and remove_empty_field
            # Returns the relationship after sanitzing
            $scope.relationship
        # Validate the given value: it must be unique, no other field should have it
        $scope.isValidFieldName = (verbose_name, field, fields=$scope.relationship.fields)->
            # Do not test emty value
            return yes if verbose_name is '' or not verbose_name?
            # For better sustainability, different case is not allowed too
            name = toFieldName(verbose_name).toLowerCase()
            # Find a field with the same name?
            not _.find(fields, (f)-> f.name.toLowerCase() is name and f isnt field)?
        # Add a field
        $scope.addField = ->
            field = angular.copy
                name: ""
                verbose_name: ""
                type: "string"
            $scope.relationship.fields.push field
        # Remove a field
        $scope.removeField = (field)->
            index = _.indexOf $scope.relationship.fields, (f)-> f.name is field.name
            delete $scope.relationship.fields[index]
            $scope.relationship.fields.splice(index, 1)
        # True if the given type is allowed
        $scope.isAllowedType = (field)-> FIELD_TYPES.indexOf( do field.type.toLowerCase ) > -1
        # Shortcut to the model object
        $scope.relationship = angular.copy($scope.relationshipForm or {})
        $scope.relationship = $scope.sanitizeRelationship no, yes
        # Original model
        $scope.master = $scope.relationshipForm
        # Add default fields
        $scope.relationship.fields = [] unless $scope.relationship.fields?
        # Field that will be added to the list
        do $scope.addField unless $scope.relationship.fields.length
        # Sanitize the model automaticly
        $scope.$watch "relationship", (-> do $scope.sanitizeRelationship), yes
    ]
