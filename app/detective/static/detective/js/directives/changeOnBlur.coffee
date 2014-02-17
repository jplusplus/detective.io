# override the default input to update on blur
# Thanks to http://stackoverflow.com/questions/11868393/angularjs-inputtext-ngchange-fires-while-the-value-is-changing
angular.module('detective.directive').directive "changeOnBlur", ->
    restrict: "A"
    require: "ngModel"
    link: (scope, elm, attr, ngModelCtrl) ->
        return  if attr.type is "radio" or attr.type is "checkbox"
        elm.unbind("input").unbind("keydown").unbind "change"
        elm.bind "blur", ->
            scope.$apply ->
                ngModelCtrl.$setViewValue elm.val()
