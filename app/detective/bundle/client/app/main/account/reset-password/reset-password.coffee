angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('reset-password',
        url: "/account/reset-password/?token"
        controller: UserCtrl
        templateUrl: '/partial/main/account/reset-password/reset-password.html'
    )
]