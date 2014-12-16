angular.module('detective').directive "screenHeight", ["$window", ($window)->
    (scope, element, attrs) ->
        ev = "screenHeight resize"
        resize = ->
            element.css "height", $window.innerHeight
            element.css("min-height", 1*attrs.screenHeight) unless isNaN(attrs.screenHeight)

        do resize
        angular.element($window).bind ev, resize
        # Unbind existing scroll handler when destroying the directive
        scope.$on '$destroy', -> angular.element($window).unbind ev
]