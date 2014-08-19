(angular.module 'detective.directive').directive 'httpErrorDisplayer', ['$rootScope', '$timeout', ($rootScope, $timeout) ->
    restrict : 'A'
    link : (scope, element, attr) ->
        howManyLabels = 0

        element.addClass 'http-error-displayer'
        $rootScope.$on 'http:error', (event, message) ->
            errorLabel = angular.element '<div></div>'

            errorLabel.addClass 'label label-danger label-http-error fade in out'
            errorLabel.attr 'id', 'http-error--' + do Date.now
            errorLabel.text message

            element.append errorLabel
            ++howManyLabels

            $timeout =>
                do errorLabel.remove
                howManyLabels = Math.max 0, howManyLabels - 1
            , 6500
]