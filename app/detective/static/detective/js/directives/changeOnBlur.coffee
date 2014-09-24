# override the default input to update on blur
# Thanks to http://stackoverflow.com/questions/11868393/angularjs-inputtext-ngchange-fires-while-the-value-is-changing
angular.module('detective.directive').directive "changeOnBlur", ->
    restrict: "A"
    require: "ngModel"
    link: (scope, elm, attr, ngModelCtrl) ->
        return if attr.type is "radio" or attr.type is "checkbox"

        if attr.textAngular?
            getValue = ((input) =>
                =>
                    do input.val
            ) elm.find 'input[type="hidden"]'
            elm = elm.find '.ta-bind'
            eventOff = ['input', 'keydown', 'keyup', 'change']

        eventOn = eventOn || 'change'
        eventOff = eventOff || ['input', 'keydown', 'keyup', 'change', 'blur']
        getValue = getValue || =>
            do elm.val

        elm.off e for e in eventOff
        elm.on eventOn, ->
            scope.$apply ->
                ngModelCtrl.$setViewValue do getValue
