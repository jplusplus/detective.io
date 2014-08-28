angular.module('detective.service').factory('User', ['$cookies', '$rootScope', ($cookies, $rootScope)->
    sdo = {}
    # Function to set the value that update CSRF token and return the object
    sdo.set = (data) ->
        $.extend sdo, data, true
        unless data.user__is_logged
            $cookies.user__is_logged = null
        # Propagate changes
        $rootScope.$broadcast "user:updated", sdo
        # Return sdo explicitely
        return sdo

    sdo.isStaff = ->
        sdo.is_staff

    sdo.hasPermission = (topic, operation)->
        permission_name = "#{topic}.contribute_#{operation}"
        sdo.is_staff or _.contains(sdo.permissions, permission_name)

    sdo.hasDeletePermission = (topic)->
        sdo.hasPermission topic, 'delete'

    sdo.hasChangePermission = (topic)->
        sdo.hasPermission topic, 'change'

    sdo.hasAddPermission = (topic)->
        sdo.hasPermission topic, 'add'

    sdo.hasReadPermission = (topic) ->
        sdo.hasPermission topic, 'read'

    # Set user's values
    sdo.set(
        # Create basic user using cookies
        if $cookies.user__is_logged
            is_logged   : !! 1*$cookies.user__is_logged
            is_staff    : !! 1*$cookies.user__is_staff
            username    : $cookies.user__username or null
            permissions : []
        # set default values
        else
            is_logged   : false
            is_staff    : false
            username    : ''
            permissions : []
    )

    return sdo
])