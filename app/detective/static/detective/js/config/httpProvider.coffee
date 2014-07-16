angular.module('detective.config').config(['$httpProvider',
    ($httpProvider)->
        # Intercepts HTTP request to add cache for anonymous user
        # and to set the right csrf token from the cookies
        $httpProvider.interceptors.push('AuthHttpInterceptor')
])