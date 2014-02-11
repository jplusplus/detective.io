angular.module("detective.directive").directive "pwMatch", ->
    restrict: 'A'
    require: "ngModel"
    transclude: true
    scope:
        with: "&"
    link: (scope, elem, attrs, ctrl) ->
        # Function to check the validity of the field
        check = -> ctrl.$setValidity "pwmatch",
            # Do not check empty fields
            elem.val()   is "" or
            scope.with() is "" or
            # The two values must be the same
            elem.val()   is scope.with()
        # Watch reference attribute and current input
        scope.$watch "with()", check
        elem.on "keyup", -> scope.$apply(check)