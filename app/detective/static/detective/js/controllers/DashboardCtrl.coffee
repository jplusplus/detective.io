class DashboardCtrl
    # Injects dependancies
    @$inject: ['$scope', 'Common', 'Page', 'User', 'userTopics', 'userGroups']
    constructor: (@scope, @Common, @Page, @User, userTopics, userGroups)->
        @Page.title "Dashboard"
        # Get the user's topics
        @scope.topics = userTopics.concat _.pluck(userGroups, 'topic')

    @resolve:
        userTopics: ["Common", "User", (Common, User)->
            Common.query(type: "topic", author__username: User.username).$promise
        ],
        userGroups: ["$http", "$q", "Auth", ($http, $q, Auth)->
            deferred = $q.defer()
            Auth.load().then (user)=>
                $http.get("/api/common/v1/user/#{user.id}/groups/").then (response)->
                    deferred.resolve response.data.objects
            deferred.promise
        ]

angular.module('detective.controller').controller 'dashboardCtrl', DashboardCtrl