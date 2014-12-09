angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('page',
        url: "/page/:slug/"
        controller: PageCtrl
        # Allow a dynamic loading by setting the templateUrl within controller
        template: "<div ng-include src='templateUrl'></div>"
    )
]