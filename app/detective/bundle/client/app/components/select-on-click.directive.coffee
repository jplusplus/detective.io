angular.module('detective').directive 'selectOnClick', ->
    restrict: 'A',
    link: (scope, element, attrs)->
        element.on 'click', -> do @select