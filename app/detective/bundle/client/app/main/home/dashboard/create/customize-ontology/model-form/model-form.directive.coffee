angular.module('detective').directive "modelForm", ()->
    restrict: "A"
    templateUrl: "/partial/main/home/dashboard/create/customize-ontology/model-form/model-form.html"
    scope:
        models: "="
        modelForm: "="
        submit: "&"
        cancel: "&"
    controller: [ '$scope', ($scope)->
        FIELD_TYPES = ['string', 'richtext', 'float', 'datetime', 'url']
        # Transform the given string into a valid model name
        toModelName = (verbose_name)->
            verbose_name = getSlug verbose_name, titleCase: yes
            verbose_name.split('-').join('')
        # Transform the given string into a valid field name
        toFieldName = (verbose_name)-> getSlug verbose_name, separator: '_'
        # Sanitize the model to make it ready to be inserted
        $scope.sanitizeModel = (remove_empty_field=no, populate_empty=no)->
            if $scope.model.verbose_name?
                # Generate model name
                $scope.model.name = toModelName $scope.model.verbose_name
            # Add field array
            $scope.model.fields or= []
            # Process each field
            for field, index in $scope.model.fields
                # Skip unallowed types
                continue unless $scope.isAllowedType(field)
                # Use name as default verbose name
                field.verbose_name = field.verbose_name or field.name if populate_empty
                # Generate fields name
                field.name = toFieldName field.verbose_name
                # Field name exists?
                unless field.name? and field.name isnt ''
                    # Should we remove empty field?
                    if remove_empty_field
                        delete $scope.model.fields[index]
                        $scope.model.fields.splice index, 1
                    continue
                # Lowercase first letter
                if field.name.length < 2
                    field.name = do field.name.toLowerCase
                else
                    field.name = field.name.substring(0, 1).toLowerCase() + field.name.substring(1)
            # Returns the model after sanitizing
            $scope.model
        # Validate the given value: it must be unique, no other model should have it
        $scope.isValidModelName = (verbose_name)->
            # Do not test emty value
            return yes if verbose_name is ''
            # For better sustainability, different case is not allowed too
            name = toModelName(verbose_name).toLowerCase()
            # Find a model with the same name?
            not _.find($scope.models, (m)-> m.name.toLowerCase() is name and m isnt $scope.master)?
        # Validate the given value: it must be unique, no other field should have it
        $scope.isValidFieldName = (verbose_name, field)->
            # Do not test emty value
            return yes if verbose_name is ''
            # For better sustainability, different case is not allowed too
            name = toFieldName(verbose_name).toLowerCase()
            # Find a field with the same name?
            not _.find($scope.model.fields, (f)-> f.name.toLowerCase() is name and f isnt field)?
        # Add a field
        $scope.addField = =>
            verbose_name = if $scope.model.fields.length is 0 then "name" else ""
            field = angular.copy
                verbose_name: verbose_name
                name: toModelName verbose_name
                type: "string"
            $scope.model.fields.push field
        # Remove a field
        $scope.removeField = (field)->
            index = -1
            # Find the index of the field
            angular.forEach $scope.model.fields, (f, i)-> index = i if f.name is field.name
            # Delete the existing field
            delete $scope.model.fields[index]
            $scope.model.fields.splice(index, 1)
        # True if the given type is allowed
        $scope.isAllowedType = (field)-> FIELD_TYPES.indexOf( do field.type.toLowerCase ) > -1
        # Shortcut to the model object
        $scope.model = angular.copy $scope.modelForm or {}
        $scope.model = $scope.sanitizeModel yes, yes
        # Original model
        $scope.master = $scope.modelForm
        # Add default fields
        $scope.model.fields = [] unless $scope.model.fields?
        # Field that will be added to the list
        do $scope.addField unless $scope.model.fields.length
        # Sanitize the model automaticly
        $scope.$watch "model", ( -> do $scope.sanitizeModel ), yes
    ]
