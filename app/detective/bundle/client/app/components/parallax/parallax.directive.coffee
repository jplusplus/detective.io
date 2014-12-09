angular.module('detective').directive "parallax", ["$window", ($window)->
    restrict: "A"
    link: (scope, elm, attr) ->
        # Detect touch device to desable parallax effect
        is_touch_device = 'ontouchstart' in document.documentElement;
        # Function that move the element inside the directive
        update = ()->
            scrollTop  = wdw.scrollTop()
            # Distance from the top of the window
            fromTop   = elm.offset().top
            # Distance of the parent step from the top of the container
            delta     = scrollTop - fromTop
            # Speed of the movement
            speed     = (1*attr.speed) or 0.5
            maxOffset = (target.height() - elm.height())/2
            offset    = speed*delta
            offset    = - maxOffset if offset < - maxOffset
            offset    =   maxOffset if offset >   maxOffset
            # Overlay opacity
            opacity   = scrollTop / (fromTop + elm.height())
            # Transform the position using the right property
            target.css "transform", "translate(0, #{offset}px)"
            # Ligthen the overlay
            overlay.css "opacity", opacity
        # Initialize target position
        init = ()->
            elm.css "position", "relative"
            target.css
                top: "50%"
                position: "absolute"
                marginTop: -target.height()/2
            # First positioning of the bg
            update() unless is_touch_device
        target  = angular.element(elm).find(attr.parallax)
        overlay = angular.element(elm).find(attr.overlay)        
        # Window element
        wdw = angular.element($window)
        # Unbind existing scroll handler
        wdw.unbind "scroll.parallax resize.parallax"
        # Bind a scroll handler on the window
        wdw.bind "scroll.parallax resize.parallax", ()-> update(target, wdw) unless is_touch_device
        # Unbind existing scroll handler when destroying the directive
        scope.$on '$destroy', -> wdw.unbind "scroll.parallax resize.parallax"
        # Init again if image height change (Firefox fix)
        scope.$watch (-> target.height() ), init
        # First initialization
        init()
        # Also call init when the image is loaded
        target.on("load", init) if target.is("img")
            
]