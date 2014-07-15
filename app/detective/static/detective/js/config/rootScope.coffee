# NOTE : this is a transition file that is NOT part of the config module.
# In the future it most of its method should be delegates to ui-router's states.
angular.module('detective').run(['$rootScope', '$location', 'User', 'Page',
    ($rootScope, $location, user, Page)->
        # Location available within templates
        $rootScope.location  = $location;
        $rootScope.user      = user
        $rootScope.Page      = Page
        # Update global render
        $rootScope.is404 = (is404)->
            # Value given
            if is404?
                # Set the 404
                $rootScope._is404 = is404
                # Disabled loading
                Page.loading false if is404
            $rootScope._is404

        $rootScope.is403 = (is403) ->
            if is403?
                $rootScope._is403 = is403
                Page.loading false if is403
            $rootScope._is403

        $rootScope.$on "$routeChangeStart", ->
            $rootScope.is404 no
            $rootScope.is403 no

        # Helper checking if any 400+ error is set
        $rootScope.is40X = -> $rootScope._is404 || $rootScope._is403
])