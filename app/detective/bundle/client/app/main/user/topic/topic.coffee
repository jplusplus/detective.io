angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('user-topic',
        url: "/:username/:topic/"
        controller: UserTopicCtrl
        resolve:
            topic: UserTopicCtrl.resolve.topic
        # Allow a dynamic loading by setting the templateUrl within controller
        template: "<div ng-include src='templateUrl' ng-if='templateUrl'></div>"
    )
]