angular.module('detective.directive').directive('ontologyVisualization', ['$timeout', ($timeout) ->
    link: (scope, elem, attrs)->
        relayout = =>
            $timeout =>
                # positioning around a circle
                models_nui = elem.find(".model")
                radius     = (Math.min(elem.width(), elem.height()) / 2)
                width      = elem.width()
                height     = elem.height()
                angle      = 0
                step       = (2 * Math.PI) / models_nui.length
                models_nui.each ->
                    x = Math.round(width  / 2 + radius * Math.cos(angle) - $(this).width()  / 2)
                    y = Math.round(height / 2 + radius * Math.sin(angle) - $(this).height() / 2)
                    $(this).css
                        left: x
                        top : y
                    angle += step
                # relationships
                jsPlumb.reset()
                for model in scope.models
                    for field in model.fields
                        if field.type == "relationship"
                            model_name = model.name
                            related_to = field.related_model
                            jsPlumb.connect
                                source: "model#{model_name}"
                                target: "model#{related_to}"
                                connector:"StateMachine"
                                paintStyle:
                                    lineWidth: 2
                                    strokeStyle: "#1B2024"
                                hoverPaintStyle:
                                    strokeStyle:"#1B2024"
                                endpoint: "Blank"
                                anchor: "Continuous"
                                overlays:[
                                    [
                                        "PlainArrow", {
                                            location:1,
                                            width:10,
                                            length:12
                                        }
                                    ],
                                    [
                                        "Label", {
                                            label:"#{field.verbose_name}",
                                            location:.5,
                                            cssClass:"label",
                                            id:"label--#{field.related_name}"
                                        }
                                    ]
                                ]
                jsPlumb.draggable jsPlumb.getSelector(".model"),
                    containment: elem

        #DOM has finished rendering
        scope.$watch 'models', relayout, true

])
# EOF