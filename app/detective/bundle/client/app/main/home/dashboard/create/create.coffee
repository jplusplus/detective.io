angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('user-topic-create',
        url: '/create/'
        controller: CreateTopicCtrl
        reloadOnSearch: no
        templateUrl: '/partial/main/home/dashboard/create/create.html'
        resolve: CreateTopicCtrl.resolve
    )
]
