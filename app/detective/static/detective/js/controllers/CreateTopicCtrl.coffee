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
        datasets: ['$q', 'Page', 'TopicDataSet', ($q, Page, TopicDataSet) ->
            deferred = do $q.defer
            notFound = ->
                do deferred.reject
                $state.go "404"
                deferred
            forbidden = ->
                do deferred.reject
                $state.go "403"
                deferred
            Page.loading yes
            TopicDataSet.get (data) =>
                deferred.resolve data
            deferred.promise
        ]

    @$inject: TopicFormCtrl.$inject.concat ['$rootScope', '$timeout', '$location', 'User', 'skeletons', 'datasets']

    # Note: The 4 first parameters need to stay in that order if we want the
    # `super` call to work properly (TopicFormCtrl.new.apply(this, arguments))
    constructor: (@scope, @state, @TopicsFactory, @Page, @EVENTS, @rootScope, @timeout, @location, @User, skeletons, datasets)->
        super
        @setCreatingMode()
        @scope.skeletons = skeletons
        @scope.selected_skeleton = {}
        @scope.all_datasets = datasets
        @scope.selected_dataset = {}
        @scope.topic = {}
        @scope.goToPlans = @goToPlans
        @scope.selectSkeleton = @selectSkeleton
        @scope.isSelected = @isSelected
        @scope.isTeaserSkeleton = @isTeaserSkeleton
        @scope.hasSelectedSkeleton = @hasSelectedSkeleton
        @scope.shouldShowForm = @hasSelectedSkeleton

        if @userMaxReached()
            @scope.max_reached = true
            @scope.plan_name  = @User.profile.plan
            @scope.topics_max  = @User.profile.topics_max
            @scope.topics_count  = @User.profile.topics_count
        @scope.user = @User

        @Page.title "Create a new investigation"
        @scope.$on @EVENTS.skeleton.selected, @onSkeletonSelected

    # nav & scope methods
    goToPlans: =>
        @state.go 'plans'

    selectSkeleton: (skeleton)=>
        unless @isTeaserSkeleton(skeleton)
            @scope.selected_skeleton = skeleton
            @rootScope.$broadcast @EVENTS.skeleton.selected
        else
            @goToPlans()

    isTeaserSkeleton: (skeleton)=>
        has_free_plan = @User.profile.plan is 'free'
        has_free_plan and skeleton.enable_teasing

    isSelected: (skeleton)=>
        return false unless @scope.selected_skeleton?
        skeleton.id == @scope.selected_skeleton.id

    hasSelectedSkeleton: =>
        @scope.selected_skeleton? and @scope.selected_skeleton.id?

    onSkeletonSelected: =>
        # safe init
        @scope.topic = @scope.topic or {}
        # binding to skeleton will automaticaly bind the skeleton ontolgy
        # to this new topic in API.
        @scope.topic.topic_skeleton = @scope.selected_skeleton.id
        @scope.topic.about = @scope.selected_skeleton.picture_credits
        # Angular scroll
        @location.search({scrollTo: 'topic-form'})
        @timeout(=>
                @rootScope.$broadcast @EVENTS.trigger.scroll
            , 250
        )

    userMaxReached: =>
        profile = @User.profile
        return false if profile.topics_max < 0 # unlimited plans
        profile.topics_count >= profile.topics_max

    create: ()=>
        @scope.loading = yes
        @TopicsFactory.post(@scope.topic, (topic)=>
            @rootScope.$broadcast @EVENTS.topic.created
            @scope.loading = no
            @state.go 'user-topic',
                username: topic.author.username
                topic: topic.slug
        , (response)=>
            @scope.loading = no
            # BAD REQUEST
            if response.status is 400
                @scope.error = response.data.topic
            # UNAUTHORIZED
            if response.status is 401
                @scope.error = "Your not authorized to perform this action."
        )


angular.module('detective.controller').controller 'createTopicCtrl', CreateTopicCtrl