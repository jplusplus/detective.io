angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('404-page',
        url: "/404/"
        controller: NotFoundCtrl
        templateUrl: '/partial/main/404/404.html'
    )
    .state('404',
        controller: NotFoundCtrl
        templateUrl: '/partial/main/404/404.html'
    )
]