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
            elm = elm.find '.ta-editor'
            event = 'blur'

        event = event || 'change'
        getValue = getValue || =>
            do elm.val

        elm.unbind("input").unbind("keydown").unbind("change")
        elm.bind event, ->
            scope.$apply ->
                ngModelCtrl.$setViewValue do getValue
