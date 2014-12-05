angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('activate',
        url: "/account/activate/?token"
        controller: UserCtrl
        templateUrl: '/partial/main/account/activation/activation.html'
    )
]