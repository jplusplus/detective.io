angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('user-topic-create.manual',
        templateUrl: '/partial/main/home/dashboard/create/manual/manual.html'
    )
]