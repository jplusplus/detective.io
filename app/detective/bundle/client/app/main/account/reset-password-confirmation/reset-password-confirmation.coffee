angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('reset-password-confirm',
        url: "/account/reset-password-confirm/?token"
        controller: UserCtrl
        templateUrl: '/partial/main/account/reset-password-confirmation/reset-password-confirmation.html'
    )
]