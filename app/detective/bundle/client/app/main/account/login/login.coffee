angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('login',
        url: "/login/?nextState&nextParams"
        auth: false # authenticated users cannot access this page
        controller: LoginCtrl
        templateUrl: '/partial/main/account/login/login.html'
    )
]