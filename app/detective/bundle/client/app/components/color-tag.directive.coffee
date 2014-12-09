angular.module('detective').directive "colorTag", ["$filter", ($filter)->
    template: "<span class='color-tag'></span>"
    replace : true
    scope   :
        ref: "&"
    link    : (scope, element, attrs) ->
        element.css "background-color", $filter("strToColor")(scope.ref())
]