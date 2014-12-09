angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('user-topic-list',
        url: '/:username/:topic/:type/?page'
        controller: IndividualListCtrl
        templateUrl: "/partial/main/user/topic/type/type.html"
        reloadOnSearch: true
        resolve:
            topic: UserTopicCtrl.resolve.topic
    )
]