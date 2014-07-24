(angular.module 'detective.service').factory 'HttpErrorInterceptor', ['$q', '$rootScope', ($q, $rootScope) =>
    responseError : (rejection) =>
        $rootScope.$broadcast 'http:error', rejection.status + ' ' + rejection.statusText
        $q.reject rejection
]