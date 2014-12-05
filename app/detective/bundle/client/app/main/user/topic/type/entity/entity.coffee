angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('user-topic-detail',
        url: '/:username/:topic/:type/:id/'
        controller: IndividualSingleCtrl
        templateUrl: "/partial/main/user/topic/type/entity/entity.html"
        reloadOnSearch: true
        resolve:
            topic: UserTopicCtrl.resolve.topic
            forms: UserTopicCtrl.resolve.forms
            individual: UserTopicCtrl.resolve.individual
    )
]