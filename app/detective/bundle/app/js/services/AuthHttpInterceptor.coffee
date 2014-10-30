angular.module('detective.service').factory('AuthHttpInterceptor', [ '$q', '$cookies', 'User', ($q, $cookies, User)->
    request: (config)->
        config = config or $q.when(config)
        config.cache = config.cache or not User.is_logged
        # Add CSRF Token for post request
        if $cookies.csrftoken?
            config.headers = config.headers or {}
            config.headers['X-CSRFToken'] = $cookies.csrftoken
        # do something on success
        return config
])
