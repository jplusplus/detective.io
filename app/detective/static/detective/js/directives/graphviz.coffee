(angular.module 'detective').directive "graphviz", ['$filter', '$window' , '$routeParams', ($filter, $window, $routeParams) ->
    restrict: "AE"
    template : "<div></div>"
    replace : yes
    scope :
        nodes : '='
        topic : '='
    link: (scope, element, attr) ->
        scope.$watch 'nodes', ->

            return if not scope.nodes.length

            do element.empty

            graph = ((((((do d3.layout.force).size [800, 600]).linkDistance 120).gravity 0.05)
                .charge -2000).friction 0.1).linkStrength 0.8

            nodes = do scope.nodes.slice
            links = ({source:0,target:i} for i in [1..nodes.length - 1])

            bilinks = []
            links.forEach (link) ->
                source = nodes[link.source]
                target = nodes[link.target]
                inter = {}
                nodes.push inter
                links.push {source:source, target:inter}, {source:inter, target:target}
                bilinks.push [source,inter,target]

            do ((graph.nodes nodes).links links).start

            svg = (d3.select element[0]).append 'svg'
            svg.attr 'width', 800
            svg.attr 'height', 600

            link = (((do ((svg.selectAll '.link').data bilinks).enter).append 'path')
                .attr 'class', 'link')

            node = (((((do ((svg.selectAll '.node').data scope.nodes).enter).append 'circle')
                .attr 'class', 'node').attr 'r', 30)
                .style 'stroke', (d) -> ($filter "strToColor") d.type)
                .style 'fill', (d) -> ($filter "strToColor") d.type
            node.on 'click', (d) ->
                path = "/#{$routeParams.topic}/#{do d.type.toLowerCase}/#{d.id}"
                $window.location.href = path
            # node.on 'mouseover', (d) ->
            #     (svg.selectAll '.link').attr 'class', (link) ->
            #         if link[0].index is d.index or link[2].index is d.index then 'link hover' else 'link'
            # node.on 'mouseleave', (d) -> (svg.selectAll '.link.hover').attr 'class', 'link'

            #node.call graph.drag

            graph.on 'tick', ->
                link.attr 'd', (d) ->
                    """
                    M#{d[0].x},#{d[0].y}
                    S#{d[1].x},#{d[1].y}
                     #{d[2].x},#{d[2].y}
                    """

                (node.attr 'cx', (d) -> d.x).attr 'cy', (d) -> d.y
]