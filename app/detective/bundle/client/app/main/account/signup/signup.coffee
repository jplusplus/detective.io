angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('signup',
        url: "/signup/?email"
        auth: false # authenticated users cannot access this page
        controller: UserCtrl
        templateUrl: '/partial/main/account/signup/signup.html'
    ).state('signup-invitation'
        url: "/signup/:token/"
        controller: UserCtrl
        templateUrl: '/partial/main/account/signup/signup.html'
    )
]