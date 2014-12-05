(angular.module 'detective').directive 'autofill', [ ->
    require : 'ngModel'
    restrict : 'A'
    link : (scope, element, attr, ngModel) ->
        scope.$on 'autofill:update', ->
            ngModel.$setViewValue(element.val())
]