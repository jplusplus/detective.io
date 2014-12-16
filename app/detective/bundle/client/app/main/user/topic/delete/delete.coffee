angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('user-topic-delete',
        url: "/:username/:topic/delete/"
        controller: DeleteTopicCtrl
        templateUrl: '/partial/main/user/topic/delete/delete.html'
        resolve:
            topic: UserTopicCtrl.resolve.topic
        auth: true
        owner: true
    )
]