angular.module('detective').directive 'emptyOn', ->
    restrict: 'A'
    require: 'ngModel'
    link: (scope, element, attr, ngModel)->
        scope.$parent.$on attr.emptyOn, ->
            element.val('')
            ngModel.$setViewValue('')
            ngModel.$setPristine()
