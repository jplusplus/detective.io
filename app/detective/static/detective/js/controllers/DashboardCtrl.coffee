class DashboardCtrl
    # Injects dependancies
    @$inject: ['$scope', 'Common', 'Page', 'User', 'userTopics']
    constructor: (@scope, @Common, @Page, @User, userTopics)->
        @Page.title "Dashboard"
        # Get the user's topics
        @scope.userTopics = userTopics

    @resolve:
        userTopics: ["Common", "User", (Common, User)->
            Common.query(type: "topic", author__username: User.username).$promise
        ],
        userContributions: ["$http", "$q", "Auth", ($http, $q, Auth)->
            deferred = $q.defer()
            Auth.load().then (user)=>
                $http.get("/api/common/v1/user/#{user.id}/groups/").then (groups)->
                    deferred.resolve groups
            deferred.promise
        ]

angular.module('detective.controller').controller 'dashboardCtrl', DashboardCtrl