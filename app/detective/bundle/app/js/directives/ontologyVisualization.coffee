angular.module('detective.directive').directive('ontologyVisualization', ['$timeout', ($timeout) ->
    scope:
        models: "="
    link: (scope, elem, attrs)->
        # Create a local instance of jsPlumb (for each directive)
        plumb = jsPlumb.getInstance()
        # Redraw the connections between models and move the models
        scope.redraw = redraw = =>
            # DOM has finished rendering
            $timeout =>
                # Remove every existing relationships
                plumb.reset()
                # Find every model
                models_nui = elem.find(".model")
                # Calculate layout sizes
                radius     = (Math.min(elem.width(), elem.height()) / 2)
                width      = elem.width()
                height     = elem.height()
                angle      = 0
                step       = (2 * Math.PI) / models_nui.length                
                # And move the models arround the center
                models_nui.each ->
                    x = Math.round(width  / 2 + radius * Math.cos(angle) - $(this).width()  / 2)
                    y = Math.round(height / 2 + radius * Math.sin(angle) - $(this).height() / 2)
                    $(this).css
                        left: x
                        top : y
                    angle += step
                # Look into each model
                for model in scope.models
                    # And each fields of the model
                    for field in model.fields
                        # If the field describes a relationship
                        if field.type == "relationship"
                            model_name = model.name
                            related_to = field.related_model
                            # We create a new connection between 
                            # the model_name and the related_mode
                            plumb.connect
                                source: elem.find("[data-identifier='#{model_name}']")
                                target: elem.find("[data-identifier='#{related_to}']")
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
                                            id:"label--#{field.name}"
                                        }
                                    ]
                                ]
                # Make every model draggable      
                plumb.draggable plumb.getSelector(".model"),
                    containment: elem

        # Redraw every time we change the models array
        scope.$watch 'models', redraw, true
])
# EOF