angular.module('detective').directive "scrollTo", ->
    (scope, element, attrs) ->
        scroll = ()->
            $(window).scrollTo element, attrs.scrollTo or 0, ->
                if attrs.reset?
                    # Reset a given variable
                    scope.$parent[attrs.reset] = false
                    scope.$parent.$apply()
        scope.$watch "$last", scroll
