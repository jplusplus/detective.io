angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('user.settings',
        auth: true
        controller: AccountSettingsCtrl
        url: 'settings/'
        templateUrl: '/partial/main/account/settings/settings.html'
        default: 'home'
    )
]