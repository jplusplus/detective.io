class window.DashboardCtrl
    # Injects dependancies
    @$inject: ['$scope', '$q', '$http', '$modal', 'Common', 'Page', 'User', 'userGroups']
    constructor: (@scope, @q, @http, @modal, @Common, @Page, @User, @userGroups)->
        @Page.title "Dashboard"
        # Start to page 1, obviously
        @page = 1
        # Get the user's topics
        @scope.topics = @getTopics()
        @scope.user = @User
        # Scope methods
        @scope.hasNext = @hasNext
        @scope.hasPrevious = @hasPrevious
        @scope.nextPage = @nextPage
        @scope.previousPage = @previousPage
        @scope.openLeaveModal = @openLeaveModal

    # Concatenates @userTopics's objects with @userGroups's topics
    getTopics: =>
        _.pluck(@userGroups.objects, 'topic')

    hasNextGroups: (p=@page)=> @userGroups.meta.total_count > (@userGroups.meta.limit * p)
    hasNext: (p=@page)=> @hasNextGroups(p)
    hasPrevious: (p=@page)=> p > 1

    # Load next page
    nextPage: => @loadPage(@page+1).then (topics)=> @scope.topics = topics
    # Load previous page
    previousPage: => @loadPage(@page-1).then (topics)=> @scope.topics = topics

    openLeaveModal: (topic)=>
        @modalInstance = @modal.open
            templateUrl: '/partial/topic.leave-modal.html'
            controller : 'leaveTopicModalCtrl as modal'
            resolve:
                topic: -> topic

        @modalInstance.result.then (quitted) =>
            if quitted
                @loadPage().then (topics)=>
                    @scope.topics = topics

    loadPage: (page=@page)=>
        @scope.loading = true
        @page = page
        deferred = @q.defer()
        # Load the value at the same time
        @q.all([
            @loadUserGroups(page),
        # Get the 3 resolve promises
        ]).then (results)=>
            @userGroups = results[0]
            @scope.loading = false
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
        @http.get("/api/detective/common/v1/user/#{@User.id}/groups/?page=#{page}").then (response)->
            # Only keep data object
            response.data

    @resolve:
        userGroups: ["$http", "$q", "Auth", ($http, $q, Auth)->
            deferred = $q.defer()
            Auth.load().then (user)=>
                $http.get("/api/detective/common/v1/user/#{user.id}/groups/").then (response)->
                    deferred.resolve response.data
            deferred.promise
        ]

angular.module('detective.controller').controller 'dashboardCtrl', DashboardCtrl