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

        update = (graph) ->
            return if not scope.nodes.data?

            # Extract nodes and links from data
            id_mapping = {}
            nodes = []
            links = []
            recurse = (node, root) ->
                if not id_mapping[node.data.id]?
                    nodes.push node.data
                    id_mapping[node.data.id] = nodes.length - 1
                if root?
                    links.push {source:id_mapping[root],target:id_mapping[node.data.id]}
                if node.link?
                    node.link.reduce ((i, n) ->
                        recurse n, node.data.id
                    ), 0
            recurse(scope.nodes)

            do ((graph.nodes nodes).links links).start

            svg = ((d3.select element[0]).append 'svg').attr
                width : size[0]
                height : size[1]

            # Begin real D3 work
            tooltip = ((d3.select element[0]).append 'div').attr 'class', 'tooltip'

            defs = (svg.append 'svg:defs')
            for node in nodes
                if node.image?
                    pattern = (defs.append 'svg:pattern').attr 'id', "pattern#{node.id}"
                    ((pattern.attr 'x', '0').attr 'y', '0').attr 'patternUnits', 'objectBoundingBox'
                    (pattern.attr 'width', '1').attr 'height', '1'
                    image = (pattern.append 'svg:image').attr 'xlink:href', node.image
                    (image.attr 'x', 0).attr 'y', 0
                    size = if parseInt(node.id) is parseInt($routeParams.id) then 80 else 60
                    (image.attr 'width', size).attr 'height', size

            # Create all links
            link = (((do ((svg.selectAll '.link').data links).enter).append 'svg:line')
                .attr 'class', 'link')

            # Create all nodes
            node = (do svg.selectAll('.node').data(nodes).enter).append('svg:a')
                .attr('xlink:href', (d) -> "/#{$routeParams.topic}/#{do d.type.toLowerCase}/#{d.id}")
                .append('svg:circle').attr('class', 'node').attr('r', (d) ->
                    if parseInt(d.id) is parseInt($routeParams.id) then 40 else 30)
                .style({
                    'fill' : (d) ->
                        if d.image?
                            return 'url(' + absUrl + '#pattern' + d.id + ')'
                        return ''
                    'stroke' : (d) -> ($filter "strToColor") d.type})

            # Nodes behavior on mouseover
            node.on 'mouseover', (d) ->
                (svg.selectAll '.link').attr 'class', (link) ->
                    if link.source.index is d.index or link.target.index is d.index then 'link hover' else 'link'
                ((do tooltip.transition).duration 200).style 'opacity', .9
                tooltip.html "#{d.type} ##{d.id} : #{d.name}"
                tooltip.style 'left', "#{d3.event.layerX}px"
                tooltip.style 'top', "#{d3.event.layerY}px"
            node.on 'mouseleave', (d) ->
                ((do tooltip.transition).duration 200).style 'opacity', 0
                (svg.selectAll '.link.hover').attr 'class', 'link'

            # Make nodes draggables
            node.call graph.drag

            graph.on 'tick', ->
                (link.attr 'x1', (d) -> d.source.x).attr 'y1', (d) -> d.source.y
                (link.attr 'x2', (d) -> d.target.x).attr 'y2', (d) -> d.target.y
                (node.attr 'cx', (d) -> d.x).attr 'cy', (d) -> d.y

        graph = ((((((do d3.layout.force).size size).linkDistance 140).gravity 0.05)
            .charge -2000).friction 0.1)

        scope.$watch 'nodes', ->
            update graph

]