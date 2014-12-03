(angular.module 'detective.directive').directive "graphviz", ['$filter', '$stateParams', '$state', '$location', '$window',  'localStorageService', ($filter, $stateParams, $state, $location, $window, localStorageService)->
    restrict: "AE"
    template: "<div></div>"
    replace : yes
    scope   :
        data: '='
        clustering: '='
        embed: "="
    link: (scope, element, attr)->
        # Constant to reconize aggregation node
        AGGREGATION_TYPE = '__aggregation_bubble'
        # Minimum leaf size
        LEAF_SIZE        = 6
        # This key is used to retreive the leaf's positions from the localstorage
        LS_LEAFS_KEY     = "leaf_positions"
        # Worker SRC
        src = angular.element('.topic__single__graph__worker script').attr("src")
        src = src.slice ((src.indexOf window.STATIC_URL) + window.STATIC_URL.length)
        # Instanciate the graph Worker
        worker = new Worker "/proxy/" + src
        absUrl = do $location.absUrl
        # Data arrays
        leafs = []
        edges = []
        # The SVG size follows its container
        svgSize = null
        # Not yet define but globally available
        d3Svg = d3Defs = d3Drag = d3Graph = null
        d3Grads = d3Edges = d3Leafs = d3Labels = null
        # Maximum nodes weight according the current data
        maxNodeWeight = 1
        # Maximum links weight according the current data
        maxLinkWeight = 1

        init = ->
            # The SVG size follows its container
            svgSize = [ element.width(), element.height() ]
            # D3 elements instancies
            d3Svg = d3.select(element[0]).append 'svg'
            d3Defs = d3Svg.insert 'svg:defs', 'path'
            d3Graph = d3.layout.force().size(svgSize).charge(-300)
            d3Drag = d3Graph.drag()
            d3Grads = d3Defs.selectAll("linearGradient")
            # Resize the svg
            d3Svg.attr width: svgSize[0], height : svgSize[1]
            # User events
            d3Drag.on "dragstart", leafDragstart
            d3Drag.on "dragend", leafDragend
            d3Graph.on 'tick', graphTick
            # The worker send new data
            worker.addEventListener 'message', workerMessage
            # Update graph when there is some data
            scope.$watch 'data', => do update if scope.data

        # This experimental feature try to use the localstorage to remember
        # where the user moved a given leaf.
        #
        # This position is saved in indices and has a context
        # (which is a node page). This way we allow the user to keep consistancy
        # in the positioning of the node
        leafSavedPositions = ->
            pos = localStorageService.get(LS_LEAFS_KEY) or {}
            # Save the leaf positions of no value is given
            localStorageService.set LS_LEAFS_KEY, pos unless pos.length
            # Simply returns the positions
            pos


        # The context is simply the current state param id
        # or a global context key if we are not inside a single page
        getContext = ->
            if $stateParams.id?
                'context__node--' + $stateParams.id
            else
                'context__all'

        # Save the position of the given leaf (according its datum)
        # in the localstorage
        saveLeafPosition =  (d)->
            # Only for node with an id
            return unless d._id?
            # Get all position
            pos = do leafSavedPositions
            # Retreive the position for this leaf in this context
            pos[d._id] = {} unless pos[d._id]?
            # Add a sub key according the context
            pos[d._id][ do getContext ] =
                # Position are indices
                x: d.x/svgSize[0]
                y: d.y/svgSize[1]
            # Then save positions updated
            localStorageService.set LS_LEAFS_KEY, pos

        # The position of a single leaf inside localstorage
        getLeafPosition = (d)->
            # Get all position
            leafSavedPositions()[ d._id ] if d?

        workerMessage = (message)->
            switch message.data.type
                when 'update'
                    register message.data.data.leafs, message.data.data.edges
                when 'log'
                    console.log message

        typeColor = (d)->
            if d._type is AGGREGATION_TYPE
                "#fff"
            else
                $filter("strToColor")(d._type)

        d3GradsPosition = ->
            d3Grads
                .attr "x1", (d)-> d.source.x
                .attr "y1", (d)-> d.source.y
                .attr "x2", (d)-> d.target.x
                .attr "y2", (d)-> d.target.y

        # Is the given id the current node
        isCurrent = (id)=>
            parseInt($stateParams.id) is parseInt(id)

        edgeUpdate = (d)->
            datumX = d.target.x - d.source.x
            datumY = d.target.y - d.source.y
            datumR = Math.sqrt (datumX * datumX + datumY * datumY)
            "M#{d.source.x},#{d.source.y}A#{datumR},#{datumR} 0 0,1 #{d.target.x},#{d.target.y}"

        leafUpdate = (d)-> "translate(#{d.x}, #{d.y})"

        leafClick = (d)->
            # Check if we're dragging the leaf
            return if d3.event.defaultPrevented
            # Check if we clicked on a aggregation bubble
            if d._type is AGGREGATION_TYPE
                worker.postMessage
                    type : 'get_from_leaf'
                    data : d
            else if not isCurrent(d)
                # Build the URL
                u =
                    username: $stateParams.username
                    topic   : $stateParams.topic
                    type    : d._type.toLowerCase()
                    id      : d._id
                # URL paths
                url = "/#{u.username}/#{u.topic}/#{u.type}/#{u.id}/"
                # Naviguate in the graph for embed
                url = "/embed" + url if attr.embed?
                $location.url url
                # We're in a d3 callback so we need to manually
                # $apply the scope
                do scope.$apply

        leafEnter = (d)->
            # Do not change current node
            unless isCurrent(d._id)
                d3Svg.select(".leaf-name[data-id='#{d._id}']").attr("class", "leaf-name")

        leafLeave = (callback=angular.noop)->
            (d)->
                d3Svg.select(".leaf-name[data-id='#{d._id}']").attr("class", callback)

        leafDragstart = (d)->
            d3.select(@).classed("fixed", d.fixed = yes)

        leafDragend = (d)->
            do forceTick
            # Then save the leaf position
            saveLeafPosition d

        forceTick = ->
            do d3Graph.start
            for i in [0..Math.min(70, leafs.length*10)] then do d3Graph.tick
            do d3Graph.stop

        graphTick =  ()->
            d3Leafs.each (d)->
                d.x = Math.max LEAF_SIZE, (Math.min svgSize[0] - LEAF_SIZE, d.x)
                d.y = Math.max LEAF_SIZE, (Math.min svgSize[1] - LEAF_SIZE, d.y)
                null
            d3Edges.attr 'd', edgeUpdate
            d3Leafs.attr 'transform', leafUpdate
            d3Labels.attr 'transform', leafUpdate
            do d3GradsPosition

        createPattern = (d, d3Defs)->
            _leafSize = if (isCurrent d._id) then (LEAF_SIZE * 2) else LEAF_SIZE
            pattern   = d3Defs.append 'svg:pattern'
            pattern.attr
                id           : "pattern#{d._id}"
                x            : 0
                y            : 0
                patternUnits : 'objectBoundingBox'
                width        : 1
                height       : 1
            (pattern.append 'svg:rect').attr
                x      : 0
                y      : 0
                width  : _leafSize * 2
                height : _leafSize * 2
            null

        update = =>
            # It's useless to process if we do not have any leaf
            return if not scope.data.leafs?
            # Extract leafs and edges from data
            leafs = []
            for id, leaf of scope.data.leafs
                scope.data.leafs[id]._index = leafs.length
                leafs.push scope.data.leafs[id]
            edges = []
            for edge in scope.data.edges
                if scope.data.leafs[edge[0]]? and scope.data.leafs[edge[2]]?
                    edges.push
                        source : scope.data.leafs[edge[0]]
                        target : scope.data.leafs[edge[2]]
                        _type : edge[1]

            # Clustering deactivate, skip the worker initialization
            if not scope.clustering and scope.data.length > 70
                return register leafs, edges
            # Initialize a worker to cluster leafs
            worker.postMessage
                type : 'init'
                data :
                    current_id : $stateParams.id
                    leafs : leafs
                    edges : edges

        register = (new_leafs=[], new_edges=[])=>
            leafs = new_leafs
            edges = new_edges
            for edge in edges
                for key in ['source', 'target']
                    edge[key] = _.findWhere leafs, _id : edge[key]._id
            for leaf, i in leafs
                savedPosition = getLeafPosition leafs[i]
                # Has a position in this context?
                if savedPosition? and savedPosition[ do getContext ]?
                    # Fix the node
                    leafs[i].fixed = yes
                    # Extract its position
                    leafs[i].x = leafs[i].px = savedPosition[ do getContext ].x * svgSize[0]
                    leafs[i].y = leafs[i].py = savedPosition[ do getContext ].y * svgSize[1]
                else
                    if isCurrent leafs[i]._id
                        # Fix the current node too (it will stay at the center)
                        leafs[i].fixed = yes
                    # Move every node at the center
                    leafs[i].x = leafs[i].px = svgSize[0]/2
                    leafs[i].y = leafs[i].py = svgSize[1]/2
            do d3Update

        d3Update = =>
            d3Graph.linkDistance(100).nodes(leafs).links(edges).start()
            # Calculate the maximum link's weight
            maxLinkWeight = d3.max d3Graph.links(), (d)-> d.source.weight + d.target.weight
            # Calculate the maximum node's weight
            maxNodeWeight = d3.max d3Graph.nodes(), (d)-> d.weight
            # Calculate the size according the maximum node's weight value
            opacityScale  = d3.scale.linear().range([0.2, 1]).domain([2, maxLinkWeight])
            # Calculate opacity according the maximum link's weight value
            sizeScale     = d3.scale.linear().range([LEAF_SIZE, 40]).domain([1, maxNodeWeight])
            # Calculate the link distance according theire weights
            linkDistance  = (d)-> 100 + sizeScale(d.target.weight + d.source.weight)
            # Calculate the class of the given leaf name
            getGradID     = (d)-> "linkGrad-" + d.source._id + "-" + d.target._id
            getArrowID    = (d)-> "linkArrow-" + d.source._id + "-" + d.target._id
            sourceColor   = (d)-> typeColor(d.source)
            targetColor   = (d)-> typeColor(d.target)
            leafNameClass = (d)->
                classes = ["leaf-name"]
                if isCurrent d._id
                    classes.push "leaf-name--current"
                else if sizeScale(d.weight) <= LEAF_SIZE
                    classes.push "leaf-name--small"
                # Return all classes as string
                classes.join " "

            # Use a scale to calculate the distance
            d3Graph.linkDistance(linkDistance)

            d3Grads = d3Grads.data d3Graph.links()
            # stretch to fit
            d3Grads.enter().append("linearGradient").attr("id", getGradID ).attr "gradientUnits", "userSpaceOnUse"
            # erase any existing <stop> elements on update
            d3Grads.html("").append("stop").attr("offset", "0%").attr "stop-color", sourceColor
            d3Grads.append("stop").attr("offset", "100%").attr "stop-color", targetColor


            d3Defs.selectAll("arrow")
                .data(d3Graph.links(), getArrowID)
                .enter()
                    .append('marker')
                    .attr
                        id : getArrowID
                        class: 'arrow'
                        viewBox : "0 -5 10 10"
                        refX : 15
                        refY : -1.5
                        fill: (d)-> typeColor(d.target)
                        markerWidth : LEAF_SIZE
                        markerHeight : LEAF_SIZE
                        orient : "auto"
                    .style 'opacity', (d)-> opacityScale d.source.weight + d.target.weight
                    .append 'path'
                        .attr 'd', "M0,-5L10,0L0,5"

            # Create all new edges
            d3Edges = d3Svg.selectAll('.edge').data edges, (d)->
                d.source._id + '-' + d._type + '-' + d.target._id

            d3Edges.enter()
                .insert 'svg:path', 'circle'
                .attr 'class', 'edge'
                .attr 'd', edgeUpdate
                .attr 'marker-end', (d)-> if d.target._type isnt AGGREGATION_TYPE then 'url(' + absUrl + '#' + getArrowID(d) + ')' else ''
                .style 'stroke', (d)->  "url(" + absUrl + "#" + getGradID(d) + ")"
                .style 'stroke-opacity', (d)->  opacityScale d.source.weight + d.target.weight

            # Remove old edges
            d3Edges.exit().remove()
            # Create all new leafs
            d3Leafs = d3Svg.selectAll('.leaf').data leafs, (d)-> d._id
            d3Leafs.enter()
                .insert('svg:circle', 'text')
                    .attr 'class', 'leaf'
                    .attr 'r', (d)-> sizeScale(d.weight)
                    .style 'fill', typeColor
                    .each (d)-> createPattern d, d3Defs
                    .call d3Drag
            # Remove old leafs
            d3Leafs.exit().remove()
            # Ensure that all existing label are deleted
            d3Svg.selectAll('.leaf-name-wrapper').remove()
            # Create all new labels
            d3Labels = d3Svg.selectAll('.leaf-name-wrapper').data leafs, (d)-> d._id
            # Remove any existing label
            d3Labels.enter()
                .append('svg:foreignObject')
                    .attr "class", "leaf-name-wrapper"
                    .attr "requiredFeatures", "http://www.w3.org/TR/SVG11/feature#Extensibility"
                    .attr 'width', 150
                    .attr 'height', 28
                    .attr 'x', 150/-2
                    .attr 'y', (d)-> - 28 - sizeScale(d.weight)
                    .append "xhtml:div"
                        .text (d)-> d.name
                        .attr 'class', leafNameClass
                        .attr 'data-id', (d)-> d._id
            # Remove old labels
            d3Labels.exit().remove()
            # Pre-calculate positions
            do forceTick
            # Display name on hover
            d3Leafs.on 'mouseenter', leafEnter
            d3Leafs.on 'mouseleave', leafLeave(leafNameClass)
            d3Leafs.on 'click',      leafClick

        # Everything is declared, let's go!
        do init

]