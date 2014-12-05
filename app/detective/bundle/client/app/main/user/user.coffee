angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('user',
        url: "/:username/"
        template: '<ui-view/>'
        controller: ['Auth', 'User', '$state', '$stateParams', (Auth, User, $state, $stateParams) =>
            unless $state.includes("user.*")
                if (do Auth.isAuthenticated) and User.username is $stateParams.username
                    $state.go 'user.me', { username: $stateParams.username }
                else
                    $state.go 'user.notme', { username: $stateParams.username }
        ]
    ).state('user.notme',
        controller: UserProfileCtrl
        templateUrl: "/partial/main/user/user.html"
        default: 'user'
        resolve:
            user: UserCtrl.resolve.user
            userGroups: ['Group', '$q', 'user', (Group, $q, user)->
                deferred = $q.defer()
                UserProfileCtrl.loadGroups(Group, user, 1).then (results)->
                    deferred.resolve results
                deferred.promise
            ]
            topics: [ 'userGroups', (userGroups)->
                UserProfileCtrl.getTopics userGroups
            ]
    )
    .state('user.me',
        auth: true
        controller: UserProfileCtrl
        templateUrl: "/partial/main/user/user.html"
        default: 'user'
        resolve:
            user: UserCtrl.resolve.user
            userGroups: ['Group', '$q', 'user', (Group, $q, user)->
                deferred = $q.defer()
                UserProfileCtrl.loadGroups(Group, user, 1).then (results)->
                    deferred.resolve results
                deferred.promise
            ]
            topics: [ 'userGroups', (userGroups)->
                UserProfileCtrl.getTopics userGroups
            ]
    )
]