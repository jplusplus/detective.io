angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('user-topic-create.describe',
        templateUrl: '/partial/main/home/dashboard/create/describe/describe.html'
    )
]