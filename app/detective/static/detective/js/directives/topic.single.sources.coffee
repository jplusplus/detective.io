# this directive help us to display a display popover for our sources
angular.module('detective.directive').directive 'sourcesPopover', [ 'UtilsFactory', (UtilsFactory)->
        restrict: "AE"
        templateUrl: "partial/topic.single.sources.html"
        replace: true
        scope:
            fieldSources: '=sourcesList'
            orientation: '=?sourcesPopoverOrientation'

        link: (scope, elem, attrs)->
            scope.isSourceURLValid = (source)=>
                UtilsFactory.isValidURL(source.reference)

    ]
