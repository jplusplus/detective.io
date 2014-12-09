angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('user-topic-detail.network',
        url: 'network/'
        templateUrl: "/partial/main/user/topic/type/entity/network/network.html"
    )
]