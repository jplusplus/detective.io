angular.module('detectiveServices').factory('User', ['$cookies', '$http', '$timeout', ($cookies, $http, $timeout)->  
    sdo = {}
    # Function to set the value that update CSRF token and return the object
    sdo.set = (data)-> 
        $.extend sdo, data, true         
        # Wait a short delay because angular's $cookies
        # isn't updated in real time
        $timeout ->
            # Add CSRF Token for post request
            if $cookies.csrftoken?          
                $http.defaults.headers.common['X-CSRFToken'] = $cookies.csrftoken             
        , 250
        # Return sdo explicitely
        return sdo
    sdo.hasPermission = (scope, operation)->
        authorized = sdo.is_staff or _.contains(sdo.permissions,"#{scope}.contribute_#{operation}")
        return authorized

    # Set user's values and returns it
    sdo.set(
        # Create basic user using cookies
        if $cookies.user__is_logged
            is_logged   : $cookies.user__is_logged 
            is_staff    : $cookies.user__is_staff 
            username    : $cookies.user__username or ''
            permissions : $cookies.user__permissions or []
        # set default values
        else
            is_logged   : false 
            is_staff    : false
            username    : ''
            permissions : []
    )

])