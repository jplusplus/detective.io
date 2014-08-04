(angular.module 'detective.service').factory 'HttpErrorInterceptor', ['$q', '$rootScope', ($q, $rootScope) =>
    responseError : (rejection) =>
        if rejection.status >= 400
            if typeof(rejection.data) is 'string' and rejection.data.length
                message = rejection.data
            else
                message = "Bear with us, something went wrong here."
                if rejection.status is 403
                    message = "Sorry, you dont have access rights here."
                else if rejection.status is 404
                    message = "Bummer, the thing you searched for does not exist."
            $rootScope.$broadcast 'http:error', message
        $q.reject rejection
]