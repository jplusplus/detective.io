angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('home',
        url: "/"
        template: '<ui-view/>'
        controller: ["Auth", "$state", (Auth, $state)->
            if $state.is("home")
                if Auth.isAuthenticated()
                    $state.go "home.dashboard"
                else
                    $state.go "home.tour"
        ]
    )
]
