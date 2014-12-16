angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('user-topic-contribute',
        url: '/:username/:topic/contribute/?id&type'
        controller: ContributeCtrl
        templateUrl: "/partial/main/user/topic/contribute/contribute.html"
        resolve:
            forms: UserTopicCtrl.resolve.forms
            topic: UserTopicCtrl.resolve.topic
        auth: true
    )
]