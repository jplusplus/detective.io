# took from http://stackoverflow.com/a/14837021/885541
angular.module('detective.directive').directive 'focusOn', ($timeout) ->
    scope: 
        trigger: '=focusOn' 
    link: (scope, element) ->
        scope.$watch 'trigger', (value)->
            if value is true
                console.log 'should focus to ', element
                element[0].focus()
                scope.trigger = false
