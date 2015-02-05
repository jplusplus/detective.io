angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('user-topic-create.manual.describe',
        templateUrl: '/partial/main/home/dashboard/create/manual/describe/describe.html'
    )
]