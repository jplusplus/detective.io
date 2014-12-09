angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('user-topic-search',
        url: '/:username/:topic/search/?q&page'
        controller: IndividualSearchCtrl
        templateUrl: "/partial/main/user/topic/type/type.html"
        reloadOnSearch: true
        resolve:
            topic: UserTopicCtrl.resolve.topic
    )
]