class DashboardCtrl
    # Injects dependancies
    @$inject: ['$scope', '$q', '$http', 'Common', 'Page', 'User', 'userTopics', 'userGroups']
    constructor: (@scope, @q, @http, @Common, @Page, @User, @userTopics, @userGroups)->
        @Page.title "Dashboard"
        # Start to page 1, obviously
        @page = 1
        # Get the user's topics
        @scope.topics = @getTopics()
        # Scope methods
        @scope.hasNext = @hasNext
        @scope.hasPrevious = @hasPrevious
        @scope.nextPage = @nextPage
        @scope.previousPage = @previousPage

    # Concatenates @userTopics's objects with @userGroups's topics
    getTopics: =>
        @userTopics.objects.concat _.pluck(@userGroups.objects, 'topic')

    hasNextTopics: (p=@page)=> @userTopics.meta.total_count > (@userTopics.meta.limit * p)
    hasNextGroups: (p=@page)=> @userGroups.meta.total_count > (@userGroups.meta.limit * p)
    hasNext: (p=@page)=> @hasNextTopics(p) or @hasNextGroups(p)
    hasPrevious: (p=@page)=> p > 1

    # Load next page
    nextPage: => @loadPage(@page+1).then (topics)=> @scope.topics = topics
    # Load previous page
    previousPage: => @loadPage(@page-1).then (topics)=> @scope.topics = topics

    loadPage: (page=@page)=>
        @page = page
        deferred = @q.defer()
        # Load the value at the same time
        @q.all([
            @loadUserTopics(page),
            @loadUserGroups(page),
        # Get the 3 resolve promises
        ]).then (results)=>
            @userTopics = results[0]
            @userGroups = results[1]
            deferred.resolve @getTopics()
        # Returns a promises
        deferred.promise

    loadUserTopics: (page)=>
        params =
            type: "topic"
            author__username: @User.username,
            offset: (page-1)*20
        @Common.get(params).$promise

    loadUserGroups: (page)=>
        @http.get("/api/common/v1/user/#{@User.id}/groups/?page=#{page}").then (response)->
            # Only keep data object
            response.data

    @resolve:
        userTopics: ["Common", "User", (Common, User)->
            Common.get(type: "topic", author__username: User.username).$promise
        ],
        userGroups: ["$http", "$q", "Auth", ($http, $q, Auth)->
            deferred = $q.defer()
            Auth.load().then (user)=>
                $http.get("/api/common/v1/user/#{user.id}/groups/").then (response)->
                    deferred.resolve response.data
            deferred.promise
        ]

angular.module('detective.controller').controller 'dashboardCtrl', DashboardCtrl