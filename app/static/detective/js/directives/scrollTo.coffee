angular.module('detective').directive "scrollTo", ->
    (scope, element, attrs) ->
        scope.$watch "$last", () ->
            $(window).scrollTo(element, attrs.scrollTo or 0)