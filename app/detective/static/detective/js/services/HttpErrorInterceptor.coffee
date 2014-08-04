(angular.module 'detective.service').factory 'HttpErrorInterceptor', ['$q', '$rootScope', ($q, $rootScope) =>
    responseError : (rejection) =>
        if rejection.status >= 400
            if typeof(rejection.data) is 'string' and rejection.data.length
                message = rejection.data
            else
                message = rejection.status + ' ' + rejection.statusText
            $rootScope.$broadcast 'http:error', message
        $q.reject rejection
]