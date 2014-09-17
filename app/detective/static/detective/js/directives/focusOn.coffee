# took from http://stackoverflow.com/a/14837021/885541
angular.module('detective.directive').directive 'focusOn', ($timeout) ->
    link: (scope, element, attrs) ->
        getTrigger = ->
            scope.$eval attrs.focusOn
        scope.$watch getTrigger, (value)->
            console.log 'focus-on trigger value changed !', value
            if value is true
                $timeout ->
                    $(element[0]).focus()
                    scope[attrs.focusOn] = false if scope[attrs.focusOn]?

