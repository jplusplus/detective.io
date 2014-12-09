(angular.module 'detective').directive 'httpErrorDisplayer', ['$rootScope', '$timeout', '$document', ($rootScope, $timeout, $document) ->
    restrict : 'A'
    link : (scope, element, attr) ->
        howManyLabels = 0

        element.addClass 'http-error-displayer'
        $rootScope.$on 'http:error', (event, message) ->
            now = do Date.now

            errorLabel = angular.element '<div></div>'

            errorLabel.addClass 'label label-danger label-http-error fade in out'
            errorLabel.attr 'id', 'http-error--' + now
            errorLabel.text message

            element.append errorLabel
            ++howManyLabels

            cleanError = =>
                do errorLabel.remove
                howManyLabels = Math.max 0, howManyLabels - 1

            _timeout = $timeout =>
                do cleanError
                $document.off "click.http-error-#{now}"
            , 6500

            $document.on "click.http-error-#{now}", (e) ->
                $timeout.cancel _timeout
                do cleanError
]