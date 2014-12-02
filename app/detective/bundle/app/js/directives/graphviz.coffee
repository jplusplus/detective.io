(angular.module 'detective.directive').directive "graphviz", ['$filter', '$stateParams', '$location', '$rootScope', 'Individual', ($filter, $stateParams, $location, $rootScope, Individual)->
    restrict: "AE"
    template: "<div></div>"
    replace : yes
    scope   :
        data : '='
        clustering : '='
    link: (scope, element, attr)->
        src             = (angular.element '.topic__single__graph__worker script')[0].src
        src             = src.slice ((src.indexOf window.STATIC_URL) + window.STATIC_URL.length)
        worker          = new Worker "/proxy/" + src
        absUrl          = do $location.absUrl
        leafSize        = 6
        svgSize         = [ element.width(), element.height() ]
        d3Svg           = ((d3.select element[0]).append 'svg')
            .attr
                width  : svgSize[0]
                height : svgSize[1]
        d3Defs          = d3Svg.insert 'svg:defs', 'path'
        d3Graph         = d3.layout.force().size(svgSize).charge(-300)
        aggregationType = '__aggregation_bubble'
        d3Edges         = null
        d3Leafs         = null
        d3Labels        = null
        leafs           = []
        edges           = []
        d3Drag          = d3Graph.drag()
        maxNodeWeight   = 1
        maxLinkWeight   = 1
        typeColor       = (d)-> if d._type is aggregationType then "#fff" else $filter("strToColor")(d._type)
        # Fix node after draging
        d3Drag.on "dragstart", (d)-> d3.select(@).classed("fixed", d.fixed = yes)
        d3Drag.on "dragend", (d)->
            do d3Graph.start
            for i in [0..100] then do d3Graph.tick
            do d3Graph.stop

        d3Grads = d3Defs.selectAll("linearGradient")

        d3GradsPosition = ->
            d3Grads
                .attr "x1", (d)-> d.source.x
                .attr "y1", (d)-> d.source.y
                .attr "x2", (d)-> d.target.x
                .attr "y2", (d)-> d.target.y

        # Is the given id the current node
        isCurrent = (id) => (parseInt $stateParams.id) is parseInt id

        edgeUpdate = (d)->
            datumX = d.target.x - d.source.x
            datumY = d.target.y - d.source.y
            datumR = Math.sqrt (datumX * datumX + datumY * datumY)
            "M#{d.source.x},#{d.source.y}A#{datumR},#{datumR} 0 0,1 #{d.target.x},#{d.target.y}"

        leafUpdate = (d)-> "translate(#{d.x}, #{d.y})"

        createPattern = (d, d3Defs)->
            _leafSize = if (isCurrent d._id) then (leafSize * 2) else leafSize
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
                    edge[key] = _.findWhere leafs,
                        _id : edge[key]._id
            for i in [0..(Math.min leafs.length, 3)]
                leafs[i]._shouldDisplayName = yes if leafs[i]?
            do d3Update

        worker.addEventListener 'message', (event) =>
            switch event.data.type
                when 'update'
                    register event.data.data.leafs, event.data.data.edges

        d3Update = =>
            d3Graph.linkDistance(100).nodes(leafs).links(edges).start()
            # Calculate the maximum link's weight
            maxLinkWeight = d3.max d3Graph.links(), (d)-> d.source.weight + d.target.weight
            # Calculate the maximum node's weight
            maxNodeWeight = d3.max d3Graph.nodes(), (d)-> d.weight
            # Calculate the size according the maximum node's weight value
            opacityScale  = d3.scale.linear().range([0.2, 1]).domain([2, maxLinkWeight])
            # Calculate opacity according the maximum link's weight value
            sizeScale     = d3.scale.linear().range([leafSize, 40]).domain([1, maxNodeWeight])
            # Calculate the link distance according theire weights
            linkDistance  = (d)-> 100 + sizeScale(d.target.weight + d.source.weight)
            # Calculate the class of the given leaf name
            leafNameClass = (d)-> if sizeScale(d.weight) > leafSize then "leaf-name" else "leaf-name leaf-name--small"
            getGradID     = (d)-> "linkGrad-" + d.source._id + "-" + d.target._id
            getArrowID    = (d)-> "linkArrow-" + d.source._id + "-" + d.target._id
            sourceColor   = (d)-> typeColor(d.source)
            targetColor   = (d)-> typeColor(d.target)
            # Use a scale to calculate the distance
            d3Graph.linkDistance(linkDistance)

            d3Grads = d3Grads.data(d3Graph.links(), getGradID)
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
                        markerWidth : leafSize
                        markerHeight : leafSize
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
                .attr 'marker-end', (d)-> if d.target._type isnt aggregationType then 'url(' + absUrl + '#' + getArrowID(d) + ')' else ''
                .style 'stroke', (d)->  "url(" + absUrl + "#" + getGradID(d) + ")"
                .style 'stroke-opacity', (d)->  opacityScale d.source.weight + d.target.weight

            # Remove old edges
            d3Edges.exit().remove()

            # Create all new leafs
            d3Leafs = d3Svg.selectAll('.leaf').data leafs, (d)-> d._id
            d3Leafs.enter().insert('svg:circle', 'text')
                .attr 'class', 'leaf'
                .attr 'r', (d)-> sizeScale(d.weight)
                .style 'fill', typeColor
                .each (d)-> (createPattern d, d3Defs)
                .call d3Drag
            # Remove old leafs
            d3Leafs.exit().remove()

            # Display name on hover
            d3Leafs.on 'mouseenter', (d)-> d3Svg.select(".leaf-name[data-id='#{d._id}']").attr("class", "leaf-name")
            d3Leafs.on 'mouseleave', (d)-> d3Svg.select(".leaf-name[data-id='#{d._id}']").attr("class", leafNameClass)
            d3Leafs.on 'click', (d)->
                # Check if we're dragging the leaf
                return if d3.event.defaultPrevented
                # Check if we clicked on a aggregation bubble
                if d._type is aggregationType
                    worker.postMessage
                        type : 'get_from_leaf'
                        data : d
                else
                    $location.path "/#{$stateParams.username}/#{$stateParams.topic}/#{do d._type.toLowerCase}/#{d._id}"
                    # We're in a d3 callback so we need to manually $apply the scope
                    do scope.$apply

            # Create all new labels
            d3Labels = (d3Svg.selectAll '.leaf-name-wrapper').data leafs, (d)-> d._id
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
            do d3Graph.start
            for i in [0..100] then do d3Graph.tick
            do d3Graph.stop

        d3Graph.on 'tick', =>
            d3Leafs.each (d)->
                d.x = Math.max leafSize, (Math.min svgSize[0] - leafSize, d.x)
                d.y = Math.max leafSize, (Math.min svgSize[1] - leafSize, d.y)
                null
            d3Edges.attr 'd', edgeUpdate
            d3Leafs.attr 'transform', leafUpdate
            d3Labels.attr 'transform', leafUpdate
            do d3GradsPosition

        # Update graph when there is some data
        scope.$watch 'data', => do update if scope.data
]