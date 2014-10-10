angular.module('detective.directive').directive('ontologyVisualization', ['$timeout', ($timeout) -> 
    link: (scope, elem, attrs)->
        console.log scope.models
        for model in scope.models
            for field in model.fields
                if field.type == "relationship"
                    console.log field
        $timeout =>
            #DOM has finished rendering
            jsPlumb.ready ->
                jsPlumb.connect
                    source: "model--pill",
                    target: "model--molecule",
                    endpoint:["Rectangle"
                        cssClass:"myEndpoint",
                        anchor: "AutoDefault"
                        width:30, 
                        height:10 
                    ]

                # jsPlumb.draggable $(".model"),
                #     containment: 'parent'
])