#=require TopicFormCtrl
class window.CreateTopicCtrl extends window.TopicFormCtrl
    @resolve:
        skeletons: ($state, $q, Page, TopicSkeleton)->
            notFound = ->
                do deferred.reject
                $state.go "404"
                deferred
            forbidden = ->
                do deferred.reject
                $state.go "403"
                deferred
            deferred = do $q.defer
            # Activate loading mode
            Page.loading yes
            TopicSkeleton.get (data)=>
                # Resolve the deffered result
                deferred.resolve(data)
            # Return a deffered object
            deferred.promise

    @$inject: TopicFormCtrl.$inject.concat ['$rootScope', '$timeout', '$location',  'skeletons', '$http']
    # Note: The 5 first parameters need to stay in that order if we want the
    # `super` call to work properly (TopicFormCtrl.new.apply(this, arguments))
    constructor: (@scope, @state, @TopicsFactory, @Page, @User, @EVENTS, @rootScope, @timeout, @location, skeletons, @http)->
        super
        @Page.title "Create a new data collection"
        # Scope attributes
        @scope.skeletons         = skeletons
        @scope.selected_skeleton = null
        @scope.topic             = {}
        @scope.user              = @User
        if @userMaxReached()
            @scope.max_reached  = true
            @scope.plan_name    = @User.profile.plan
            @scope.topics_max   = @User.profile.topics_max
            @scope.topics_count = @User.profile.topics_count
        # Scope methods
        @scope.selectSkeleton      = @selectSkeleton
        @scope.isSkeletonSelected  = @isSkeletonSelected
        @scope.isTeaserSkeleton    = @isTeaserSkeleton
        @scope.hasSelectedSkeleton = @hasSelectedSkeleton
        # Scope events
        @scope.$on @EVENTS.skeleton.selected, @onSkeletonSelected
        @state.go "user-topic-create"
        # Load data sample
        @http.get("static/csv/sample-bill-murray.tsv").success (data)=>
            @scope.csv = data

    selectSkeleton: (skeleton)=>
        if not skeleton?
            @scope.selected_skeleton = null
        else if not @isTeaserSkeleton(skeleton)
            @scope.selected_skeleton = skeleton
            @rootScope.$broadcast @EVENTS.skeleton.selected
        else
            @state.go('plans')

    isTeaserSkeleton: (skeleton)=>
        has_free_plan = @User.profile.plan is 'free'
        has_free_plan and skeleton.enable_teasing

    isSkeletonSelected: (skeleton)=>
        return false unless @scope.selected_skeleton?
        skeleton.id == @scope.selected_skeleton.id

    hasSelectedSkeleton: =>
        @scope.selected_skeleton? and @scope.selected_skeleton.id?

    onSkeletonSelected: =>
        # safe init
        @scope.topic = @scope.topic or {}
        # binding to skeleton will automaticaly bind the skeleton ontolgy
        # to this new topic in API.
        @scope.topic.ontology_as_json = @scope.selected_skeleton.ontology
        # Populate empty fields
        @scope.topic.about = @scope.selected_skeleton.picture_credits
        @scope.topic.background_url = @scope.selected_skeleton.picture

    userMaxReached: =>
        profile = @User.profile
        return false if profile.topics_max < 0 # unlimited plans
        profile.topics_count >= profile.topics_max

    create: (panel)=>
        @scope.loading[panel] = yes
        @TopicsFactory.post(@scope.topic, (topic)=>
            @rootScope.$broadcast @EVENTS.topic.created
            @scope.loading[panel] = no
            @state.go 'user-topic',
                username: topic.author.username
                topic: topic.slug
        , (response)=>
            @scope.loading[panel] = no
            # BAD REQUEST
            if response.status is 400
                @scope.error = response.data.topic
            # UNAUTHORIZED
            if response.status is 401
                @scope.error = "Your not authorized to perform this action."
        )


angular.module('detective').controller 'createTopicCtrl', CreateTopicCtrl
