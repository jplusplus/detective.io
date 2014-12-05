angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('subscribe'
        url: "/subscribe/?plan"
        templateUrl: '/partial/main/account/subscribe/subscribe.html'
        controller: UserCtrl
    )
]