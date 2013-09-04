# Load Django static tags (""" avoid to break coffee coloration)
"""{% load staticfiles %}"""

angular.module('detective').directive "countryMap", ($parse)->    
    compile: (tElement, tAttrs, transclude)->
        # Pre link function (build DOM)
        pre: (scope, iElement, iAttrs, controller)->
            # Create the map within iElement with the same width
            # (the height will be calculate later)
            map = $K.map( iElement, iElement.width(), iElement.width()*0.4 )
            # Load the SVG            
            map.loadMap '{% static "detective/svg/world.svg" %}'

        # Post link function (bind vent)
        post: (scope, iElement, iAttrs, controller)->