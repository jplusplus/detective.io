angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('403',
        controller: NotFoundCtrl
        templateUrl: '/partial/main/403/403.html'
    )
]