class ProfileCtrl
    # Injects dependencies
    @$inject: ['$scope', 'Common', 'Page', 'user', '$state', '$q', '$http', 'userTopics', 'userGroups']

    constructor: (@scope, @Common, @Page, @user, $state, @q, @http, @userTopics, @userGroups)->
        @Page.title @user.username
        @Page.loading no

        @topics_page = 1

        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        # Is this our profile page?
        @scope.isMe = $state.is 'user.me'
        #
        @scope.shouldShowTopics = true
        # User info
        @scope.user =
            name : "#{@user.first_name} #{@user.last_name}"
            username : @user.username
            gravatar : "http://www.gravatar.com/avatar/#{@user.email}?s=200&d=mm"
            location : @user.profile.location
            organization : @user.profile.organization
            url : @user.profile.url
        # All topics the user has access to
        @scope.topics = do @getTopics

        # ──────────────────────────────────────────────────────────────────────
        # Scope methods
        # ──────────────────────────────────────────────────────────────────────
        @scope.hasNext = @hasNext
        @scope.hasPrevious = @hasPrevious
        @scope.nextPage = @nextPage
        @scope.previousPage = @previousPage
        @scope.shoulShowValueFor = @shoulShowValueFor
        @scope.shouldShowFormFor = @shouldShowFormFor
        @scope.openFormFor = @openFormFor
        @scope.validateFormFor = @validateFormFor

        @edit =
            location : no
            organization : no
            url : no

    # Concatenates @userTopics's objects with @userGroups's topics
    getTopics: =>
        @userTopics.objects.concat (_.pluck @userGroups.objects, 'topic')

    hasNextTopics: (p=@page)=> @userTopics.meta.total_count > (@userTopics.meta.limit * p)
    hasNextGroups: (p=@page)=> @userGroups.meta.total_count > (@userGroups.meta.limit * p)
    hasNext: (p=@page)=> @hasNextTopics(p) or @hasNextGroups(p)
    hasPrevious: (p=@page)=> p > 1

    # Load next page
    nextPage: => @loadPage(@page+1).then (topics)=> @scope.topics = topics
    # Load previous page
    previousPage: => @loadPage(@page-1).then (topics)=> @scope.topics = topics

    loadPage: (page=@page) =>
        @page = page
        deferred = do @q.defer
        (@q.all [
            @loadUserTopics(page)
            @loadUserGroups(page)
        ]).then (results) =>
            @userTopics = results[0]
            @userGroups = results[1]
            do deferred.resolve
        deferred.promise

    loadUserTopics: (page) =>
        params =
            type: 'topic'
            author__id: @user.id
            offset: (page-1)*20
        (@Common.get params).$promise

    loadUserGroups: (page) =>
        (@http.get "/api/common/v1/user/#{@user.id}/groups/?page=#{page}").then (response) ->
            response.data

    canShowTopic: (topic) =>
        topic.public or @User.hasReadPermission topic.ontology_as_mod

    shoulShowValueFor: (fieldName) =>
        return yes unless @scope.isMe
        not @edit[fieldName]

    shouldShowFormFor: (fieldName) =>
        return no unless @scope.isMe
        @edit[fieldName]

    openFormFor: (fieldName) =>
        @edit[fieldName] = yes

    validateFormFor: (fieldName) =>
        data = {}
        data[fieldName] = @scope.user[fieldName]
        (@http
            method : 'patch'
            url : "/api/common/v1/profile/#{@user.profile.id}/"
            data : data
        ).then =>
            @edit[fieldName] = no

    @resolve:
        userTopics: ["Common", "User", (Common, user)->
            Common.get(type: "topic", author__id: user.id).$promise
        ],
        userGroups: ["$http", "$q", "Auth", ($http, $q, Auth)->
            deferred = $q.defer()
            Auth.load().then (user)=>
                $http.get("/api/common/v1/user/#{user.id}/groups/").then (response)->
                    deferred.resolve response.data
            deferred.promise
        ]
        user: [
            "$rootScope",
            "$stateParams",
            "$state",
            "$q",
            "Common",
            ($rootScope, $stateParams, $state, $q, Common)->
                notFound    = ->
                    deferred.reject()
                    $state.go "404"
                    deferred
                deferred    = $q.defer()
                # Checks that the current topic and user exists together
                if $stateParams.username?
                    # Retreive the topic for this user
                    params =
                        type    : "user"
                        username: $stateParams.username
                    Common.get params, (data)=>
                        # Stop if it's an unkown topic
                        return notFound() unless data.objects and data.objects.length
                        # Resolve the deffered result
                        deferred.resolve data.objects[0]
                # Reject now
                else return notFound()
                # Return a deffered object
                deferred.promise
        ]

angular.module('detective.controller').controller 'profileCtrl', ProfileCtrl
