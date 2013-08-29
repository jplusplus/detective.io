angular.module('detectiveServices').factory('User', ['$cookies', '$http', '$timeout', ($cookies, $http, $timeout)->  
    sdo = {}
    # Function to set the value that update CSRF token and return the object
    sdo.set = (data)-> 
        $.extend sdo, data, true 
        # Wait a short delay because angular's $cookies
        # isn't updated in real type
        $timeout ->
            # Add CSRF Token for post request
            if $cookies.csrftoken?
                $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken             
        , 250
        # Return sdo explicitely
        return sdo

    # Set user's values and returns it
    sdo.set(
        # Create basic user using cookies
        if $cookies.user__is_logged
            is_logged: $cookies.user__is_logged 
            is_staff : $cookies.user__is_staff 
            username : $cookies.user__username or ''
        # set default values
        else
            is_logged: false 
            is_staff : false
            username : ''
    )

])