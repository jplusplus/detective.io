angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('user-topic-invite',
        url: "/:username/:topic/invite/"
        controller: AddCollaboratorsCtrl
        templateUrl: '/partial/main/user/topic/invite/invite.html'
        resolve:
            topic: UserTopicCtrl.resolve.topic
            collaborators: AddCollaboratorsCtrl.resolve.collaborators
            administrators: AddCollaboratorsCtrl.resolve.administrators
        auth: true
        admin: yes
    )
]