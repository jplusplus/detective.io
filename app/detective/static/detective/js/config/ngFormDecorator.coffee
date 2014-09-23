# Allows to use dynamic name attribute for forms' inputs.
# took from http://plnkr.co/edit/hSMzWC?p=preview
# solution is attributed to http://github.com/caitp
# given in [this comment](https://github.com/angular/angular.js/issues/1404#issuecomment-30859987)
angular.module('detective.config').config(['$provide', ($provide)->
    $provide.decorator 'ngModelDirective', ($delegate)->
        ngModel    = $delegate[0]
        controller = ngModel.controller
        ngModel.controller = [
            '$scope'
            '$element'
            '$attrs'
            '$injector'
            (scope, element, attrs, $injector)->
                $interpolate = $injector.get('$interpolate')
                attrs.$set('name', $interpolate(attrs.name or '')(scope))
                $injector.invoke(controller, this, {
                    '$scope': scope,
                    '$element': element,
                    '$attrs': attrs
                })
        ]
        $delegate

    $provide.decorator 'formDirective', ($delegate)->
        form       = $delegate[0]
        controller = form.controller
        form.controller = [
            '$scope'
            '$element'
            '$attrs'
            '$injector'
            (scope, element, attrs, $injector)->
                $interpolate = $injector.get('$interpolate')
                attrs.$set('name', $interpolate(attrs.name or attrs.ngForm or '')(scope))
                $injector.invoke(controller, this, {
                    '$scope': scope,
                    '$element': element,
                    '$attrs': attrs
                })
        ]
        $delegate
])
