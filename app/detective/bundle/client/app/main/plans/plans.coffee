angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('plans',
        url: "/plans/"
        templateUrl: '/partial/main/plans/plans.html'
        controller: ["Page", (Page) ->
            Page.title "Paid plans"
        ]
    )
]