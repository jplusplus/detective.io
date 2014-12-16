angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('user-topic.network',
        url: "network/"
    )
]