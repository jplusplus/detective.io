HashMerge = (a={}, b={}) ->
    result = { }
    for i of a
        if (i of b) and a[i] isnt b[i]
            if (a[i] instanceof Array) and (b[i] instanceof Array)
                result[i] = a[i].concat b[i]
            else if (a[i] instanceof Object) and (b[i] instanceof Object)
                result[i] = HashMerge a[i], b[i]
            else
                result[i] = [a[i], b[i]]
        else
            result[i] = a[i]
    for i of b
        continue if i of result
        result[i] = b[i]
    result

(angular.module 'detective.directive').directive "graphviz", ['$filter', '$routeParams', '$location', '$rootScope', 'Individual', ($filter, $routeParams, $location, $rootScope, Individual)->
    restrict: "AE"
    template : "<div></div>"
    replace : yes
    scope :
        data : '='
    link: (scope, element, attr)->
        absUrl = do $location.absUrl

        leafSize = 6

        svgSize = [ element.width(), element.height() ]
        d3Svg = ((d3.select element[0]).append 'svg').attr
            width : svgSize[0]
            height : svgSize[1]
        d3Defs = d3Svg.insert 'svg:defs', 'path'

        d3Graph = (((do d3.layout.force).size svgSize).linkDistance 90).charge -300

        d3Edges = null
        d3Leafs = null
        d3Labels = null

        leafs = []
        edges = []

        aggregationType = '__aggregation_bubble'
        aggregationThreshold = 5

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

        isCurrent = (id)=> id is parseInt $routeParams.id

        getTextClasses = (datum) ->
            [
                'name'
                if not datum._shouldDisplayName then 'toggle-display' else ''
            ].join ' '

        sortAndReindex = (array) ->
            _.map (_.sortBy array, (datum) -> -datum.weight), (datum, i) ->
                datum._index = i
                datum

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
                edges.push
                    source : scope.data.leafs[edge[0]]
                    target : scope.data.leafs[edge[2]]
                    _type : edges[1]

            # Start the layout
            do ((d3Graph.nodes leafs).links edges).start

            # Sort by weight (DESC) to know which node should should always display its name
            leafs = sortAndReindex leafs
            for i in [0..(Math.min leafs.length, 3)]
                leafs[i]._shouldDisplayName = yes if leafs[i]?

            ###
            # Time to aggregate!
            ###
            do ->
                canAggregate = (leaf) ->
                    (not isCurrent leaf._id) and (leaf._type isnt aggregationType)

                # Helper function deleting a leaf and all its edges
                deleteLeaf = (leaf, sourceLeaf=null) ->
                    # We delete the leaf and reindex the array
                    leafs.splice leaf._index, 1

                    # If there's a sourceLeaf we need to move leaf in its aggregation bubble
                    if sourceLeaf?
                        if sourceLeaf._bubble
                            sourceLeaf._bubble.leafs.push leaf
                            sourceLeaf._bubble.name = "#{sourceLeaf._bubble.leafs.length} more entities"
                        else
                            console.debug "Creating an aggregation bubble for #{leaf.name}"
                            sourceLeaf._bubble =
                                leafs : [leaf]
                                _id : ''
                                _type : aggregationType
                                name : '1 more entity'
                            edges.push
                                source : sourceLeaf
                                target : sourceLeaf._bubble
                                _type : 'is_related_to+'
                            leafs.push sourceLeaf._bubble

                    do ((d3Graph.nodes leafs).links edges).start
                    sortAndReindex leafs

                    # If there is no edge to delete, we can return
                    return unless leaf.weight > 0

                    # Clean edges, one at a time
                    clean = (do ->
                        for index, edge of edges
                            # Is this edge concerning our leaf?
                            isConcerned = [edge.source._id, edge.target._id].indexOf leaf._id
                            if isConcerned >= 0
                                leafToCheck = if isConcerned is 0 then edge.target else edge.source
                                edges.splice index, 1
                                do ((d3Graph.nodes leafs).links edges).start
                                # If we deleted the last edge of a leaf, we have to delete that leaf
                                (deleteLeaf leafToCheck) if leafToCheck.weight <= 0
                                # Aaaaand, we're going back to the top
                                return no
                        # We're done!
                        return yes
                    ) while not clean

                security = 0
                clean = (do ->
                    ++security
                    for leaf in leafs
                        # Check if we need to delete a node
                        if leaf.weight > aggregationThreshold
                            # If so, we're removing the first we encounter
                            for edge in edges
                                if (edge.source._id is leaf._id) and canAggregate edge.target
                                    deleteLeaf edge.target, leaf
                                    break
                                else if (edge.target._id is leaf._id) and canAggregate edge.source
                                    deleteLeaf edge.source, leaf
                                    break
                            leafs = sortAndReindex leafs
                            # Aaaaand, we're going back to the top
                            return (if security >= 1000 then yes else no)
                        else
                            # As leafs are sorted by weight
                            # if we encounter one leaf.weight <= threshold then we
                            # don't need to iterate to the next one
                            return yes
                ) while not clean

            ###
            # Aggregation is done!
            ###

            do d3Update

        d3Update = =>
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
                    d : leafUpdate
                .style
                    fill : (datum) -> ($filter "strToColor") datum._type
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
                    [leaf] = (datum.leafs.splice 0, 1)
                    datum.name = "#{datum.leafs.length} more entities"

                    leafs.push leaf

                    do ((d3Graph.nodes leafs).links edges).start
                    sortAndReindex leafs
                    do d3Update
                else
                    $location.path "/#{$routeParams.username}/#{$routeParams.topic}/#{do datum._type.toLowerCase}/#{datum._id}"
                    # We're in a d3 callback so we need to manually $apply the scope
                    do scope.$apply

            # Create all new labels
            d3Labels = (d3Svg.selectAll '.name').data leafs, (datum) -> datum._id
            (do d3Labels.enter).append('svg:text').attr
                    d            : leafUpdate
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