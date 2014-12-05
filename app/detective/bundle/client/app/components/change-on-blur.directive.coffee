# override the default input to update on blur
# Thanks to http://stackoverflow.com/questions/11868393/angularjs-inputtext-ngchange-fires-while-the-value-is-changing
angular.module('detective').directive "changeOnBlur", ["$timeout", ($timeout)->
    restrict: "A"
    require: "ngModel"
    link: (scope, elm, attr, ngModelCtrl) ->
        return if attr.type is "radio" or attr.type is "checkbox"
        # Text angular directive follows a custom behavior
        if attr.textAngular?
            getValue = ((input) =>
                =>
                    do input.val
            ) elm.find 'input[type="hidden"]'
            # Get the textarea element
            txt = elm.find '.ta-bind'
            # Disable all events except "blur"
            txt.off e for e in ['input', 'keydown', 'keyup', 'change']
            # Watch for class change
            scope.$watch (-> elm.hasClass('focussed') ), (focussed)->
                # Set the value if the input is no more focussed
                ngModelCtrl.$setViewValue(do getValue) unless focussed
        else
            # Disable the events
            elm.off e for e in ['input', 'keydown', 'keyup', 'change', 'blur']
            # Event that triggered changes
            # Then bind event on getvalue
            elm.on 'change', ->
                # And enters angular digest to get the value
                scope.$apply -> ngModelCtrl.$setViewValue(do elm.val)
]