angular.module('detective').directive "modelForm", ()->
    restrict: "A"
    templateUrl: "/partial/main/home/dashboard/create/manual/customize-ontology/model-form/model-form.html"
    scope:
        models: "="
        modelForm: "="
        submit: "&"
        cancel: "&"
        mayLostFieldData: "&"
        mayLostModelData: "&"
    controller: [ '$scope', 'Modal', ($scope, Modal)->
        FIELD_TYPES = ['string', 'richtext', 'float', 'datetime', 'url', 'boolean']
        # Transform the given string into a valid model name
        toModelName = (verbose_name)->
            verbose_name = getSlug verbose_name, titleCase: yes
            verbose_name.split('-').join('')
        # Transform the given string into a valid field name
        toFieldName = (verbose_name)-> getSlug verbose_name, separator: '_'
        # Sanitize the model to make it ready to be inserted
        $scope.sanitizeModel = (remove_empty_field=no, populate_empty=no)->
            if $scope.model.verbose_name?
                # You may be allowed to change the name of the model
                # with no risk of loosing data
                if not $scope.mayLostModelData({model: $scope.master})
                    # Generate model name
                    $scope.model.name = toModelName $scope.model.verbose_name
            else
                $scope.model.verbose_name = ""
            # Add field array
            $scope.model.fields or= []
            # Process each field
            for field, index in $scope.model.fields
                # Skip unallowed types
                continue unless $scope.isAllowedType(field)
                # Use name as default verbose name
                field.verbose_name = field.verbose_name or field.name if populate_empty
                # You may be allowed to change the name of the field
                # with no risk of loosing data
                if not $scope.mayLostFieldData({field: field, model: $scope.master})
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
                # This field might not be changeable without risk
                else
                    # Original field
                    masterField = _.find($scope.master.fields, { name: field.name })
                    # Type changed
                    if field.type isnt masterField.type
                        # Closure function to transmit the field type
                        resetType = (field, masterField)->
                            # User cancel the change
                            (isYes)->
                                if isYes
                                    # Update the master to ask the question once
                                    masterField.type = field.type
                                else
                                    # Restore the field type
                                    field.type = masterField.type
                        # Ask confirmation
                        m = Modal("Unconvertible data will be lost. Are you sure?", "Yes, change the type")
                        # Reset (or no the field's type)
                        m.then resetType field, masterField
            # Overide verbose_name_plural value
            if $scope.model.verbose_name.substr(-1) is 'y'
                # Name finishing by an y must finish by "ies" in there pluaral form
                $scope.model.verbose_name_plural = $scope.model.verbose_name.slice(0, -1) + "ies"
            else
                $scope.model.verbose_name_plural = $scope.model.verbose_name + "s"
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
        # Original model
        $scope.master = $scope.modelForm
        # Shortcut to the model object
        $scope.model = angular.copy $scope.modelForm or {}
        $scope.model = $scope.sanitizeModel yes, yes
        # Add default fields
        $scope.model.fields = [] unless $scope.model.fields?
        # Field that will be added to the list
        do $scope.addField unless $scope.model.fields.length
        # Sanitize the model automaticly
        $scope.$watch "model", ( -> do $scope.sanitizeModel ), yes
    ]
