###
Load Django static tags
{% load staticfiles %}
###

angular.module('detective').directive "countryMap", ($parse)->    
    scope:
        # What to when clicking a country
        click: "&?"
        # Where record the country?
        model: "=?" 
        # Value to bind to the map        
        values: "=?" 
    compile: (tElement, tAttrs, transclude)->
        # The map object is localy available
        map       = null
        # Resize the map to fit to the svg
        resizeMap = (iElement)->
            ratio  = map.viewAB.height / map.viewAB.width
            height = iElement.width() * ratio
                         
            iElement.height(height)
            map.resize()            
        # Pre link function (build DOM)
        pre: (scope, iElement, iAttrs, controller)->       
            # Draw the values on the map (chloroplete)
            draw = ()->           
                values     = _.values(scope.values)     
                colorscale = new chroma.ColorScale
                    colors: ["#F2CEBA", "#EA7E44"]    
                    limits: [_.min(values), _.max(values)]

                map.getLayer("countries").style 
                    fill: (country, path) ->
                        value = scope.values[ country["iso-a3"] ] or 0
                        colorscale.getColor(value) if value
   
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
                        'stroke-width': 0.5                              
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
                # Now the layer exists...
                # if we have values to draw!
                if scope.values?
                    # Try to draw the values once
                    draw()
                    # Watch the data and the countries' layer to add data dynamicly
                    scope.$watch "values", draw, true
                

        # Post link function (bind events)
        post: (scope, iElement, iAttrs, controller)->
            # Watch for window resize to adapt the SVG sizes
            $(window).on "resize", -> resizeMap(iElement)
       