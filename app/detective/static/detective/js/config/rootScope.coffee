# NOTE : this is a transition file that is NOT part of the config module.
# In the future it most of its method should be delegates to ui-router's states.
angular.module('detective').run(['$rootScope', '$state', 'User', 'Page',
    ($rootScope, $state, user, Page)->
        # Services available within templates
        $rootScope.$state = $state
        $rootScope.user   = user
        $rootScope.Page   = Page
])