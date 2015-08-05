angular.module('detective').config ["$stateProvider", ($stateProvider)->

    unless navigator.userAgent.toLowercase().indexOf("prerender") > -1
        $stateProvider.state 'user-topic-tmf',
            url: '/detective/the-migrants-files/'
            controller: ($window)->
                $window.location.href = 'http://www.themigrantsfiles.com/'

        $stateProvider.state 'user-topic-belarus',
            url: '/detective/belarus-networks/'
            controller: ($window)->
                $window.location.href = 'http://jplusplus.github.io/belarus-networks/'

    $stateProvider.state 'user-topic',
        url: "/:username/:topic/"
        controller: UserTopicCtrl
        resolve:
            topic: UserTopicCtrl.resolve.topic
        # Allow a dynamic loading by setting the templateUrl within controller
        template: "<div ng-include src='templateUrl' ng-if='templateUrl'></div>"

]
