detective.directive "scrollTo", ->
    (scope, element, attrs) ->
        scope.$watch "$last", (v) ->
            $(window).scrollTo(element, attrs.scrollTo or 0) if v
