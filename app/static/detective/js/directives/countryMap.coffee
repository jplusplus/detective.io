###
Load Django static tags
{% load staticfiles %}
###

angular.module('detective').directive "countryMap", ($parse)->    
    scope:
        # What to when clicking a country
        click: "&click"
        # Where record the country?
        model: "=model" 
    compile: (tElement, tAttrs, transclude)->
        # The map object is localy available
        map       = null
        # Resize the map to fit to the svg
        resizeMap = (iElement)->
            ratio  = map.viewAB.height / map.viewAB.width;                
            height = iElement.width() * ratio
                         
            iElement.height(height);
            map.resize();   
            
        # Pre link function (build DOM)
        pre: (scope, iElement, iAttrs, controller)->            
            # Create the map within iElement with the same width
            # (the height will be calculate later)
            map = $K.map( iElement, iElement.width(), iElement.width()*0.4 )
            # Load the SVG            
            map.loadMap '{% static "detective/svg/world.svg" %}', ->
                # Adapt map's sizes to the SVG
                resizeMap(iElement)
                # Add layers                
                map.addLayer 'countries',
                    'name'  : 'countries'
                    'styles':
                        'stroke-width': 1                              
                        'stroke'      : '#aaa'
                        'fill'        : '#F5F5F5'                                        
                # Bind layer click
                map.getLayer('countries').on 'click', (data)->    
                    # Do we received a click function?
                    scope.click(data) if typeof(scope.click) is "function"                                 
                    # Set a model value matching to the clicked country
                    if scope.model?                       
                        scope.model = data["iso-a3"]                        
                        scope.$apply()

        # Post link function (bind events)
        post: (scope, iElement, iAttrs, controller)->
            # Watch for window resize to adapt the SVG sizes
            $(window).on "resize", -> resizeMap(iElement)