(angular.module 'detective').directive "graphviz", ['$filter', '$routeParams', '$location', ($filter, $routeParams, $location) ->
    restrict: "AE"
    template : "<div></div>"
    replace : yes
    scope :
        nodes : '='
        topic : '='
    link: (scope, element, attr) ->
        size = [element[0].clientWidth, 200]
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
            "M" + d.source.x + "," + d.source.y + "A" + dr + "," + dr + " 0 0,1 " + d.target.x + "," + d.target.y

        nodeUpdate = (d) ->
            "translate(" + d.x + "," + d.y + ")"

        update = =>
            return if not scope.nodes.data?

            # Extract nodes and links from data
            id_mapping = {}
            nodes = []
            links = []
            recurse = (node, root) ->
                if not id_mapping[node.id]?
                    if not root?
                        node.fixed = yes
                        node.x = size[0] / 2
                        node.y = size[1] / 2
                    nodes.push node
                    id_mapping[node.id] = nodes.length - 1
                if root?
                    links.push {source:id_mapping[root.id],target:id_mapping[node.id]}
                if node.children?
                    node.children.reduce ((i, n) ->
                        recurse n, node
                    ), 0
            recurse(scope.nodes)

            do ((graph.nodes nodes).links links).start

            do (svg.selectAll 'defs').remove
            defs = svg.insert 'svg:defs', 'path'
            for node in nodes
                if node.data.image?
                    pattern = defs.append 'svg:pattern'
                    pattern.attr
                        id : "pattern#{node.id}"
                        x : 0
                        y : 0
                        patternUnits : 'objectBoundingBox'
                        width : 1
                        height : 1
                    radius = if parseInt(node.id) is parseInt($routeParams.id) then 12 else 12
                    (pattern.append 'svg:rect').attr
                        x : 0
                        y : 0
                        width : radius
                        height : radius
                        fill : '#21201E'
                    image = pattern.append 'svg:image'
                    image.attr
                        'xlink:href' : node.data.image
                        x : 0
                        y : 0
                        width : radius
                        height : radius

            (((defs.append 'marker').attr
                id : 'marker-end'
                viewBox : "0 -5 10 10"
                refX : 15
                refY : -1.5
                markerWidth : 6
                markerHeight : 6
                orient : "auto").append 'path').attr 'd', "M0,-5L10,0L0,5"

            # Create all new links
            the_links = (svg.selectAll '.link').data links, (d) -> d.source.data.id + '-' + d.target.data.id
            ((do the_links.enter).insert 'svg:path', 'circle').attr
                    class : 'link'
                    d : linkUpdate
                    'marker-end' : 'url(' + absUrl + '#marker-end)'
            # Remove old links
            do (do the_links.exit).remove

            # Create all new nodes
            the_nodes = (svg.selectAll '.node').data nodes, (d) -> d.data.id
            (do the_nodes.enter).insert('svg:circle', 'text').attr('class', 'node').attr
                    r : 6
                    d : nodeUpdate
                .style
                    fill : (d) ->
                        if d.data.image?
                            return 'url(' + absUrl + '#pattern' + d.id + ')'
                        return ($filter "strToColor") d.data.type
                    stroke : (d) -> ($filter "strToColor") d.data.type
                .call graph.drag
            # Remove old nodes
            do (do the_nodes.exit).remove

            # Create all new names
            the_names = (svg.selectAll '.name').data nodes, (d) -> d.data.id
            (do the_names.enter).append('svg:text').attr
                    d : nodeUpdate
                    class : 'name'
                .text (d) -> d.data.name
            do (do the_names.exit).remove

        graph.on 'tick', =>
            the_links.attr 'd', linkUpdate
            the_nodes.attr 'transform', nodeUpdate
            the_names.attr 'transform', nodeUpdate

        scope.$watch 'nodes', =>
            update graph

]