HashMerge = (a, b) ->
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
        if i of result
            continue
        result[i] = b[i]
    result

(angular.module 'detective').directive "graphviz", ['$filter', '$routeParams', '$location', '$rootScope', 'Individual', ($filter, $routeParams, $location, $rootScope, Individual)->
    restrict: "AE"
    template : "<div></div>"
    replace : yes
    scope :
        data : '='
        topic : '='
    link: (scope, element, attr)->
        size = [element[0].clientWidth, 250]
        node_size = 6
        absUrl = do $location.absUrl

        svg = ((d3.select element[0]).append 'svg').attr
            width : size[0]
            height : size[1]

        graph = (((do d3.layout.force).size size).linkDistance 60).charge -300

        the_links = null
        the_nodes = null
        the_names = null


        linkUpdate = (d) ->
            dx = d.target.x - d.source.x
            dy = d.target.y - d.source.y
            dr = Math.sqrt (dx * dx + dy * dy)
            "M#{d.source.x},#{d.source.y}A#{dr},#{dr} 0 0,1 #{d.target.x},#{d.target.y}"

        nodeUpdate = (d) ->
            "translate(#{d.x}, #{d.y})"

        createPattern = (d, defs) ->
            _node_size = if d._id is parseInt $routeParams.id then node_size * 2 else node_size
            pattern = defs.append 'svg:pattern'
            pattern.attr
                id : "pattern#{d._id}"
                x : 0
                y : 0
                patternUnits : 'objectBoundingBox'
                width : 1
                height : 1
            (pattern.append 'svg:rect').attr
                x : 0
                y : 0
                width : _node_size * 2
                height : _node_size * 2
                fill : '#999'
            image = pattern.append 'svg:image'
            image.attr
                'xlink:href' : d.image
                x : 0
                y : 0
                width : _node_size * 2
                height : _node_size * 2
            null

        deleteNode = (d) =>
            # Make a diference between click and dblclick
            if d._timer?
                clearTimeout d._timer
                d._timer = undefined

            if d._id > 0
                delete scope.data.nodes[d._id]
            else
                delete scope.data.links[d._parent]['_AGGREGATION_']

            do update

        loadNode = (d) ->
            params =
                type  : do d._type.toLowerCase
                id    : d._id
                depth : 2
            Individual.graph params, (d) ->
                scope.data.nodes = HashMerge scope.data.nodes, d.nodes
                scope.data.links = HashMerge scope.data.links, d.links
                do update

        update = =>
            return if not scope.data.nodes?

            # Extract nodes and links from data
            nodes = (node for id, node of scope.data.nodes)
            links = []

            aggregation = 1

            _.map (_.pairs scope.data.links), ([source_id, relations]) ->
                _.map (_.pairs relations), ([relation, targets]) ->
                    if relation isnt '_AGGREGATION_'
                        _.map targets, (target_id) ->
                            if scope.data.nodes[source_id]? and scope.data.nodes[target_id]?
                                links.push
                                    source : scope.data.nodes[source_id]
                                    target : scope.data.nodes[target_id]
                                    _type : relation
                            null
                    else
                        if scope.data.nodes[source_id]?
                            nodes.push
                                _id : -(aggregation++)
                                _type : '_AGGREGATION_'
                                _parent : source_id
                                name : "#{targets.length} entities"
                            links.push
                                source : scope.data.nodes[source_id]
                                target : nodes[nodes.length - 1]
                                _type : relation
                    null
                null

            notlinked = -1
            while notlinked isnt 0
                notlinked = 0
                do ((graph.nodes nodes).links links).start

                _.map nodes, (node, i) ->
                    if node.weight is 0
                        nodes.splice i, 1
                        ++notlinked
                do ((graph.nodes nodes).links links).start

            do (svg.selectAll 'defs').remove
            defs = svg.insert 'svg:defs', 'path'

            (((defs.append 'marker').attr
                id : 'marker-end'
                viewBox : "0 -5 10 10"
                refX : 15
                refY : -1.5
                markerWidth : node_size
                markerHeight : node_size
                orient : "auto").append 'path').attr 'd', "M0,-5L10,0L0,5"

            # Create all new links
            the_links = (svg.selectAll '.link').data links, (d) ->
                d.source._id + '-' + d._type + '-' + d.target._id
            ((do the_links.enter).insert 'svg:path', 'circle').attr
                    class : 'link'
                    d : linkUpdate
                    'marker-end' : 'url(' + absUrl + '#marker-end)'
            # Remove old links
            do (do the_links.exit).remove

            # Create all new nodes
            the_nodes = (svg.selectAll '.node').data nodes, (d) -> d._id
            (do the_nodes.enter).insert('svg:circle', 'text').attr('class', 'node').attr
                    r : (d) =>
                        if d._id is parseInt $routeParams.id then node_size * 2 else node_size
                    d : nodeUpdate
                .style
                    fill : (d) ->
                        if d.image?
                            return 'url(' + absUrl + '#pattern' + d._id + ')'
                        ($filter "strToColor") d._type
                    stroke : (d) -> ($filter "strToColor") d._type
                .call(graph.drag)
                .each (d) ->
                    (createPattern d, defs) if d.image?
                    null
            # Remove old nodes
            do (do the_nodes.exit).remove

            the_nodes.on 'dblclick', deleteNode
            the_nodes.on 'click', (d) ->
                if not d._timer?
                    d._timer = setTimeout =>
                        d._timer = undefined
                        loadNode(d)
                        $rootScope.safeApply()
                    , 200

            # Create all new names
            the_names = (svg.selectAll '.name').data nodes, (d) -> d._id
            (do the_names.enter).append('svg:text').attr
                    d : nodeUpdate
                    class : 'name'
                .text (d) -> d.name
            do (do the_names.exit).remove
            null

        graph.on 'tick', =>
            the_nodes.each (d) ->
                d.x = Math.max node_size, (Math.min size[0] - node_size, d.x)
                d.y = Math.max node_size, (Math.min size[1] - node_size, d.y)
                null
            the_links.attr 'd', linkUpdate
            the_nodes.attr 'transform', nodeUpdate
            the_names.attr 'transform', nodeUpdate
            null

        scope.$watch 'data', =>
            do update
            null

        null

]