angular.module('detective').service 'Modal', ($modal)->
    (msg, yesBtn='Yes', noBtn='Cancel')->
        modal = $modal.open
            templateUrl: '/partial/components/modal/modal.html'
            controller: ['$scope', ($scope) =>
                $scope.title = msg
                $scope.buttons = yes : yesBtn, no : noBtn
                $scope.modal = modal
            ]
        return modal.result