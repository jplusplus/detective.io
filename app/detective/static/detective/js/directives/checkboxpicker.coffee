(angular.module 'detective.directive').directive 'checkboxpicker', [ ->
    restrict : 'A'
    require: "ngModel"
    link : (scope, element, attr, ngModelCtrl) ->
        if attr.default is "true"
            element.attr 'checked', true

        do element.checkboxpicker

        element.bind 'change', =>
            scope.$apply =>
                ngModelCtrl.$setViewValue element.prop 'checked'
]