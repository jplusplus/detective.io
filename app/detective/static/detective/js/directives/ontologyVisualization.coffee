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
                            source: "model--#{model_name}"
                            target: "model--#{related_to}"
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
            
        $timeout =>
            #DOM has finished rendering
            scope.$watch 'models', relayout, true

])