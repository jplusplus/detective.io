class window.UserProfileCtrl
    # Injects dependencies
    @$inject: ['$scope', 'Common', 'Page', '$state', '$q', '$http', 'user', 'Group', 'userGroups', 'topics']

    constructor: (@scope, @Common, @Page, $state, @q, @http, @user, @Group, @userGroups, topics)->
        @Page.title @user.username, no
        @topics_page = 1

        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        # Is this our profile page?
        @scope.isMe = $state.is 'user.me'
        #
        # User info
        @scope.user =
            name : "#{@user.first_name} #{@user.last_name}"
            username : @user.username
            gravatar : @user.profile.avatar
            location : @user.profile.location
            organization : @user.profile.organization
            url : @user.profile.url

        # All topics the user has access to
        @scope.topics = topics
        @scope.shouldShowTopics = true

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

    @getTopics: (groups)-> _.pluck groups.objects, 'topic'
    @loadGroups: (Group, user, page)->
        (Group.collaborator { user_id : user.id , page : page }).$promise.then (data)->
            data

    hasNextGroups: (p=@topics_page)=> @userGroups.meta.total_count > (@userGroups.meta.limit * p)
    hasNext: (p=@topics_page)=> @hasNextGroups(p)
    hasPrevious: (p=@topics_page)=> p > 1

    # Load next page
    nextPage: => @loadPage(@topics_page+1).then (topics)=> @scope.topics = topics
    # Load previous page
    previousPage: => @loadPage(@topics_page-1).then (topics)=> @scope.topics = topics

    loadPage: (page=@topics_page) =>
        @scope.loading = true
        @topics_page = page
        deferred = do @q.defer
        (@q.all [
            @loadGroups(@Group, @user, page)
        ]).then (results) =>
            @userGroups = results[0]
            @scope.loading = false
            deferred.resolve(@getTopics(@userGroups))
        deferred.promise

    loadUserTopics: (page) =>
        params =
            type: 'topic'
            author__id: @user.id
            offset: (page-1)*20
        (@Common.get params).$promise

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
        @edit[fieldName] = no
        data = {}
        data[fieldName] = @scope.user[fieldName]
        @http
            method : 'patch'
            url : "/api/detective/common/v1/profile/#{@user.profile.id}/"
            data : data

angular.module('detective.controller').controller 'userProfileCtrl', UserProfileCtrl
