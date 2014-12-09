class window.DashboardCtrl
    # Injects dependancies
    @$inject: ['$scope', '$q', '$http', '$modal', 'Common', 'Page', 'User', 'Group', 'userGroups']
    constructor: (@scope, @q, @http, @modal, @Common, @Page, @User, @Group, @userGroups) ->
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
        @scope.isAdmin = @isAdmin

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
        @Page.loading yes
        @page = page
        deferred = @q.defer()

        (@loadUserGroups page).then (results) =>
            @userGroups = results
            @Page.loading no
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
        (@Group.collaborator { user_id : @User.id , page : page }).$promise.then (data) ->
            # Only keep data object
            data

    isAdmin: (topic) =>
        (do @User.isStaff) or (@User.hasAdministratePermission topic.ontology_as_mod)

    @resolve:
        userGroups: ["$q", "Auth", "Group", ($q, Auth, Group)->
            deferred = $q.defer()
            Auth.load().then (user)=>
                (Group.collaborator { user_id : user.id }).$promise.then (data) ->
                    deferred.resolve data
            deferred.promise
        ]

angular.module('detective').controller 'dashboardCtrl', DashboardCtrl