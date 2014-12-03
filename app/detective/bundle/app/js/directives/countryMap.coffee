angular.module('detective.directive').directive "countryMap", ()->
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
                values       = _.map _.filter(scope.values, (d)-> d.count?), (d)-> d.count
                disableColor = "#fff"
                colorscale   = chroma.scale(["#978E73", "#FFE8A3"]).domain([_.min(values), _.max(values)])
                map.getLayer("countries").style
                    fill: (country, path) ->
                        item = scope.values[country["iso-a3"]]
                        if item then colorscale(item.count) else disableColor
                    stroke: (country, path) ->
                        item = scope.values[country["iso-a3"]]
                        if item then colorscale(item.count) else disableColor


            # Create the map within iElement with the same width
            # (the height will be calculate later)
            map = $K.map( iElement, iElement.width(), iElement.width()*0.4 )
            # Load the SVG
            map.loadMap "#{window.STATIC_URL}svg/world.svg", ->
                # Adapt map's sizes to the SVG
                resizeMap(iElement)
                # Add layers
                map.addLayer 'countries',
                    'name'  : 'countries'
                    'styles':
                        'stroke-width': 1
                        'stroke'      : '#BFB8A6'
                        'fill'        : '#BFB8A6'
                # Bind layer click
                map.getLayer('countries').on 'click', (data)->
                    item = scope.values[data["iso-a3"]]
                    if item?
                        # Do we received a click function?
                        scope.click() if typeof(scope.click) is "function"
                        # Set a model value matching to the clicked country
                        if scope.model? and typeof(scope.model) is "object"
                            angular.copy(item, scope.model);
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
