angular.module('detective.directive').directive('ontologyVisualization', ['$timeout', ($timeout) ->
    link: (scope, elem, attrs)->
        relayout = =>
            jsPlumb.reset()
            for model in scope.models
                for field in model.fields
                    if field.type == "relationship"
                        model_name = model.name
                        related_to = field.related_model
                        jsPlumb.connect
                            source: "model#{model_name}"
                            target: "model#{related_to}"
                            connector:"StateMachine",
                            paintStyle:{lineWidth:3,strokeStyle:"#056"}
                            hoverPaintStyle:{strokeStyle:"#dbe300"}
                            endpoint: "Blank"
                            anchor: "Continuous"
                            overlays:[
                                ["PlainArrow", {location:1, width:15, length:12} ]
                                [ "Label", { label:"#{field.verbose_name}", location:.5, cssClass:"label", id:"label--#{field.related_name}" } ]
                            ],
            jsPlumb.draggable jsPlumb.getSelector(".model"),
                drag: =>
                    console.log("DRAG")

            # Liviz
            graph = """digraph ontologygraph {\n
            graph[layout=sfdp, splines=line, overlap=prism, repulsiveforce=12, sep=5];\n
            node[shape=box, width=1.67, height=0.83];\n
            """
            for model in scope.models
                for field in model.fields
                    if field.type == "relationship"
                        model_name = model.name
                        related_to = field.related_model
                        graph += "model#{model_name} -> model#{related_to};\n"
            graph += "}"
            elem.find("textarea").html(graph)
            # digraph graph {
            #     graph[margin=1];
            #     node[shape=box, width=1.67, height=0.83];
            #     modelperson -> modelcompany;
            #     modelperson -> modelcountry;
            #     modelcompany -> modelcountry;
            # }
            window.w_launch()
        $timeout =>
            #DOM has finished rendering
            scope.$watch 'models', relayout, true

])
