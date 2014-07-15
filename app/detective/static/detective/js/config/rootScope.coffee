# NOTE : this is a transition file that is NOT part of the config module.
# In the future it most of its method should be delegates to ui-router's states.
angular.module('detective').run(['$rootScope', '$location', 'User', 'Page',
    ($rootScope, $location, user, Page)->
        # Location available within templates
        $rootScope.location  = $location;
        $rootScope.user      = user
        $rootScope.Page      = Page
])