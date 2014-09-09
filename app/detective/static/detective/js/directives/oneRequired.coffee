(angular.module 'detective.directive').directive 'oneRequired', [ ->
    restrict : 'A'
    link : (scope, element, attr) ->
        fields = attr.oneRequired.split ','

        checkValue = (value) => value? and (value isnt "")

        validationFunc = (value) =>
            valid = checkValue value
            if not valid
                for field in fields
                    valid |= checkValue scope.form[field].$modelValue
                    break if valid
            for field in fields
                scope.form[field].$setValidity field, valid
            if valid then value else undefined

        for field in fields
            scope.form[field].$parsers.unshift validationFunc
            scope.form[field].$formatters.unshift validationFunc
]