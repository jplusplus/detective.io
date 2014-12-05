angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('user-topic-contribute-upload',
        url: '/:username/:topic/contribute/upload/'
        controller: BulkUploadCtrl
        templateUrl: "/partial/main/user/topic/contribute/bulk-upload/bulk-upload.html"
        resolve:
            topic: UserTopicCtrl.resolve.topic
        auth: true
    )
]