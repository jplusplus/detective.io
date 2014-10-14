angular.module('detective.directive').directive('ontologyVisualization', ['$timeout', ($timeout) -> 
    link: (scope, elem, attrs)->

        $timeout =>
            #DOM has finished rendering
            jsPlumb.ready ->
                instance = jsPlumb.getInstance 
                    DragOptions : { cursor: "pointer", zIndex:2000 }
                    HoverClass:"connector-hover"

                for model in scope.models
                    for field in model.fields
                        if field.type == "relationship"
                            model_name = model.name
                            related_to = field.related_model
                            console.log "relationship from #{model_name} to #{related_to}.", field
                            instance.connect
                                source: "model--#{model_name}"
                                target: "model--#{related_to}"
                                connector:"StateMachine",
                                paintStyle:{lineWidth:3,strokeStyle:"#056"}
                                hoverPaintStyle:{strokeStyle:"#dbe300"}
                                endpoint: "Blank"
                                anchor: "Continuous"
                                overlays:[
                                    ["PlainArrow", {location:1, width:15, length:12} ]
                                    [ "Label", { label:"#{field.verbose_name}<br/>#{field.related_name}", location:.5, cssClass:"label", id:"label--#{field.related_name}" } ]
                                ],
                instance.draggable jsPlumb.getSelector(".model"),
                    drag: =>
                        console.log("DRAG") 

                # jsPlumb.draggable $(".model"),
                #     containment: 'parent'
])