(angular.module 'detective.directive').directive "graphviz", ['$filter', '$routeParams', '$location', '$rootScope', 'Individual', ($filter, $routeParams, $location, $rootScope, Individual)->
    restrict: "AE"
    template: "<div></div>"
    replace : yes
    scope :
        data : '='
    link: (scope, element, attr) ->
        src = (angular.element '.topic__single__graph__worker script')[0].src
        src = src.slice ((src.indexOf "{{STATIC_URL}}") + "{{STATIC_URL}}".length)
        worker = new Worker "/proxy/" + src

        absUrl = do $location.absUrl

        leafSize = 6

        svgSize = [ element.width(), element.height() ]
        d3Svg = ((d3.select element[0]).append 'svg').attr
            width : svgSize[0]
            height : svgSize[1]
        d3Defs = d3Svg.insert 'svg:defs', 'path'

        d3Graph = (((do d3.layout.force).size svgSize).linkDistance 90).charge -300

        aggregationType = '__aggregation_bubble'

        isCurrent = (id) =>
            (parseInt $routeParams.id) is parseInt id

        d3Edges = null
        d3Leafs = null
        d3Labels = null

        leafs = []
        edges = []

        edgeUpdate = (datum) ->
            datumX = datum.target.x - datum.source.x
            datumY = datum.target.y - datum.source.y
            datumR = Math.sqrt (datumX * datumX + datumY * datumY)
            "M#{datum.source.x},#{datum.source.y}A#{datumR},#{datumR} 0 0,1 #{datum.target.x},#{datum.target.y}"

        leafUpdate = (datum) ->
            "translate(#{datum.x}, #{datum.y})"

        createPattern = (datum, d3Defs) ->
            _leafSize = if (isCurrent datum._id) then (leafSize * 2) else leafSize
            pattern = d3Defs.append 'svg:pattern'
            pattern.attr
                id : "pattern#{datum._id}"
                x : 0
                y : 0
                patternUnits : 'objectBoundingBox'
                width : 1
                height : 1
            (pattern.append 'svg:rect').attr
                x : 0
                y : 0
                width  : _leafSize * 2
                height : _leafSize * 2
            null

        getTextClasses = (datum) ->
            [
                'name'
                if not datum._shouldDisplayName then 'toggle-display' else ''
            ].join ' '

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

            worker.postMessage
                type : 'init'
                data :
                    current_id : $routeParams.id
                    leafs : leafs
                    edges : edges

        worker.addEventListener 'message', (event) =>
            switch event.data.type
                when 'log' then do ->
                    # console.debug "From worker -> #{event.data.data}"
                when 'update' then do ->
                    leafs = event.data.data.leafs
                    edges = event.data.data.edges
                    for edge in edges
                        for key in ['source', 'target']
                            edge[key] = _.findWhere leafs,
                                _id : edge[key]._id
                    for i in [0..(Math.min leafs.length, 3)]
                        leafs[i]._shouldDisplayName = yes if leafs[i]?
                    do d3Update

        d3Update = =>
            do ((d3Graph.nodes leafs).links edges).start

            (((d3Defs.append 'marker').attr
                id : 'marker-end'
                class: 'arrow'
                viewBox : "0 -5 10 10"
                refX : 15
                refY : -1.5
                markerWidth : leafSize
                markerHeight : leafSize
                orient : "auto").append 'path').attr 'd', "M0,-5L10,0L0,5"

            # Create all new edges
            d3Edges = (d3Svg.selectAll '.edge').data edges, (datum) ->
                datum.source._id + '-' + datum._type + '-' + datum.target._id
            ((do d3Edges.enter).insert 'svg:path', 'circle').attr
                    class : 'edge'
                    d : edgeUpdate
                    'marker-end' : (datum) ->
                        if datum.target._type isnt aggregationType then 'url(' + absUrl + '#marker-end)' else ''
            # Remove old edges
            do (do d3Edges.exit).remove

            # Create all new leafs
            d3Leafs = (d3Svg.selectAll '.leaf').data leafs, (datum) -> datum._id
            (do d3Leafs.enter).insert('svg:circle', 'text').attr('class', 'leaf').attr
                    r : (datum) -> leafSize * ( 1 + (isCurrent datum._id) )
                .style
                    fill : (datum) -> if (datum._type is aggregationType) then '#fff' else ($filter "strToColor") datum._type
                .each (datum) ->
                    (createPattern datum, d3Defs)
                    null
                .call d3Graph.drag
            # Remove old leafs
            do (do d3Leafs.exit).remove

            # Display name on hover
            d3Leafs.on 'mouseenter', (datum) -> d3Svg.select(".name[data-id='#{datum._id}']").attr("class", "name")
            d3Leafs.on 'mouseleave', (datum) -> d3Svg.select(".name[data-id='#{datum._id}']").attr("class", getTextClasses)
            d3Leafs.on 'click', (datum) ->
                # Check if we're dragging the leaf
                return if d3.event.defaultPrevented
                # Check if we clicked on a aggregation bubble
                if datum._type is aggregationType
                    worker.postMessage
                        type : 'get_from_leaf'
                        data : datum
                else
                    $location.path "/#{$routeParams.username}/#{$routeParams.topic}/#{do datum._type.toLowerCase}/#{datum._id}"
                    # We're in a d3 callback so we need to manually $apply the scope
                    do scope.$apply

            # Create all new labels
            d3Labels = (d3Svg.selectAll '.name').data leafs, (datum) -> datum._id
            (do d3Labels.enter).append('svg:text').attr
                    dy           : (datum) -> - leafSize * ( 1 + (isCurrent datum._id) )
                    'data-id'    : (datum) -> datum._id
                    class        : getTextClasses
                    'text-anchor': "middle"
            (d3Svg.selectAll '.name').text (datum) -> datum.name
            # Remove old labels
            do (do d3Labels.exit).remove
            null

        d3Graph.on 'tick', =>
            d3Leafs.each (datum) ->
                datum.x = Math.max leafSize, (Math.min svgSize[0] - leafSize, datum.x)
                datum.y = Math.max leafSize, (Math.min svgSize[1] - leafSize, datum.y)
                null
            d3Edges.attr 'd', edgeUpdate
            d3Leafs.attr 'transform', leafUpdate
            d3Labels.attr 'transform', leafUpdate
            null

        scope.$watch 'data', =>
            do update
            null

        null

]