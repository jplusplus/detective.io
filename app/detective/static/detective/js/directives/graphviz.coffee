(angular.module 'detective').directive "graphviz", ['$filter', '$routeParams', '$location', ($filter, $routeParams, $location) ->
    restrict: "AE"
    template : "<div></div>"
    replace : yes
    scope :
        nodes : '='
        topic : '='
    link: (scope, element, attr) ->
        size = [element[0].clientWidth, 600]
        absUrl = do $location.absUrl

        svg = ((d3.select element[0]).append 'svg').attr
            width : size[0]
            height : size[1]

        graph = ((((((do d3.layout.force).size size).linkDistance 140).gravity 0.05)
            .charge -2000).friction 0.1)

        the_links = null
        the_nodes = null

        update = =>
            return if not scope.nodes.data?

            # Extract nodes and links from data
            id_mapping = {}
            nodes = []
            links = []
            recurse = (node, root) ->
                if not id_mapping[node.id]?
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

            # Begin real D3 work
            tooltip = ((d3.select element[0]).append 'div').attr 'class', 'tooltip'

            do (svg.selectAll '*').remove

            defs = (svg.append 'svg:defs')
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
                    image = pattern.append 'svg:image'
                    size = if parseInt(node.id) is parseInt($routeParams.id) then 80 else 60
                    image.attr
                        'xlink:href' : node.data.image
                        x : 0
                        y : 0
                        width : size
                        height : size

            # Create all links
            the_links = (svg.selectAll '.link').data links
            ((do the_links.enter).append 'svg:line').attr
                class : 'link'
                rel : (d) -> d.target.id + ' - ' + d.source.id

            # Create all nodes
            the_nodes = (svg.selectAll '.node').data nodes
            (do the_nodes.enter).append('svg:circle').attr('class', 'node').attr('r', (d) ->
                    if parseInt(d.id) is parseInt($routeParams.id) then 40 else 30)
                .style
                    'fill' : (d) ->
                        if d.data.image?
                            return 'url(' + absUrl + '#pattern' + d.id + ')'
                        return ''
                    'stroke' : (d) -> ($filter "strToColor") d.data.type

            # Nodes behavior on mouseover
            the_nodes.on 'mouseover', (d) ->
                # Highlight links
                (svg.selectAll '.link').attr 'class', (link) ->
                    if link.source.index is d.index or link.target.index is d.index then 'link hover' else 'link'
                # Display tooltip
                ((do tooltip.transition).duration 200).style 'opacity', .9
                tooltip.html "#{d.data.type} ##{d.id} : #{d.data.name}"
                tooltip.style
                    left : "#{d3.event.layerX}px"
                    top : "#{d3.event.layerY}px"
            the_nodes.on 'mouseleave', (d) ->
                ((do tooltip.transition).duration 200).style 'opacity', 0
                (svg.selectAll '.link.hover').attr 'class', 'link'

            # Make nodes draggables
            the_nodes.call graph.drag

        graph.on 'tick', =>
            the_links.attr
                x1 : (d) -> d.source.x
                y1 : (d) -> d.source.y
                x2 : (d) -> d.target.x
                y2 : (d) -> d.target.y
            the_nodes.attr
                cx : (d) -> d.x
                cy : (d) -> d.y

        scope.$watch 'nodes', =>
            update graph

]

###
.append('svg:a')
                .attr('xlink:href', (d) -> "/#{$routeParams.topic}/#{do d.type.toLowerCase}/#{d.id}")
###