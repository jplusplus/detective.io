angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('user-topic-edit',
        url: "/:username/:topic/settings/"
        controller: EditTopicCtrl
        templateUrl: '/partial/main/user/topic/settings/settings.html'
        resolve:
            topic: UserTopicCtrl.resolve.topic
        auth: true
        owner: true
    )
]