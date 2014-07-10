# this directive help us to display a display popover for our sources
angular.module('detective.directive').directive 'fieldSourcesList', [ 'UtilsFactory', (UtilsFactory)->
        restrict: "AE"
        templateUrl: "partial/topic.single.sources.html"
        transclude: yes
        scope:
            fieldSources: '=fieldSourcesList'
            orientation: '=?'

        link: (scope, elem, attrs)->
            scope.orientation =  scope.orientation || 'up'
            
            scope.isSourceURLValid = (source)=>
                UtilsFactory.isValidURL(source.reference)

    ]
