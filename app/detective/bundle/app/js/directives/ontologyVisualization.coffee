angular.module('detective.directive').directive('ontologyVisualization', ['$timeout', ($timeout) ->
    link: (scope, elem, attrs)->

        relayout = =>
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

# set to false the validator if the value already exist in the names of fields of the given object
angular.module('detective.directive').directive('isUniqueInFieldsNameFrom', ->
    require: 'ngModel',
    restrict : "A"
    scope:
        isUniqueInFieldsNameFrom : "="
    link: (scope, elem, attrs, ctrl) ->
        ctrl.$parsers.unshift((viewValue) ->
            if scope.isUniqueInFieldsNameFrom.fields?
                for field in scope.isUniqueInFieldsNameFrom.fields
                    if field.name == viewValue
                        ctrl.$setValidity('isNotUnique', false)
                        return viewValue
            ctrl.$setValidity('isNotUnique', true)
            return viewValue
        )
)

# EOF
