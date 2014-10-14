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

    @$inject: TopicFormCtrl.$inject.concat ['$rootScope', '$timeout', '$location',  'skeletons', 'datasets']

    # Note: The 5 first parameters need to stay in that order if we want the
    # `super` call to work properly (TopicFormCtrl.new.apply(this, arguments))
    constructor: (@scope, @state, @TopicsFactory, @Page, @User, @EVENTS, @rootScope, @timeout, @location, skeletons, datasets)->
        super
        @setCreatingMode()

        @scope.skeletons = skeletons
        @scope.selected_skeleton = {}

        @scope.all_datasets = datasets
        @scope.datasets = []
        @scope.selected_dataset = {}

        @scope.topic = {}

        @scope.goToPlans = @goToPlans
        @scope.selectSkeleton = @selectSkeleton
        @scope.selectDataSet = @selectDataSet
        @scope.isSkeletonSelected = @isSkeletonSelected
        @scope.isDataSetSelected = @isDataSetSelected
        @scope.isTeaserSkeleton = @isTeaserSkeleton
        @scope.hasSelectedSkeleton = @hasSelectedSkeleton
        @scope.hasSelectedDataSet = @hasSelectedDataSet
        @scope.shouldShowDataSets = @hasSelectedSkeleton
        @scope.shouldShowForm = => (do @hasSelectedSkeleton) and (do @hasSelectedDataSet)

        if @userMaxReached()
            @scope.max_reached  = true
            @scope.plan_name    = @User.profile.plan
            @scope.topics_max   = @User.profile.topics_max
            @scope.topics_count = @User.profile.topics_count
        @scope.user = @User

        @Page.title "Create a new investigation"

        @scope.$on @EVENTS.skeleton.selected, @onSkeletonSelected
        @scope.$on @EVENTS.dataset.selected, @onDataSetSelected

    # nav & scope methods
    goToPlans: =>
        @state.go 'plans'

    selectSkeleton: (skeleton)=>
        unless @isTeaserSkeleton(skeleton)
            @scope.selected_skeleton = skeleton
            @rootScope.$broadcast @EVENTS.skeleton.selected
        else
            @goToPlans()

    selectDataSet: (dataset) =>
        @scope.selected_dataset = dataset
        @rootScope.$broadcast @EVENTS.dataset.selected

    isTeaserSkeleton: (skeleton)=>
        has_free_plan = @User.profile.plan is 'free'
        has_free_plan and skeleton.enable_teasing

    isSkeletonSelected: (skeleton)=>
        return false unless @scope.selected_skeleton?
        skeleton.id == @scope.selected_skeleton.id

    isDataSetSelected: (dataset) =>
        return no unless @scope.selected_dataset? and @scope.selected_dataset.id?
        dataset.id is @scope.selected_dataset.id

    hasSelectedSkeleton: =>
        @scope.selected_skeleton? and @scope.selected_skeleton.id?

    hasSelectedDataSet: =>
        @scope.selected_dataset? and @scope.selected_dataset.id?

    onSkeletonSelected: =>
        # safe init
        @scope.topic = @scope.topic or {}
        # binding to skeleton will automaticaly bind the skeleton ontolgy
        # to this new topic in API.
        @scope.topic.topic_skeleton = @scope.selected_skeleton.id
        @scope.topic.about = @scope.selected_skeleton.picture_credits
        # Filter datasets
        @scope.datasets = do @getFilteredDataSets
        # Angular scroll
        @location.search({scrollTo: 'topic-datasets'})
        @timeout(=>
                @rootScope.$broadcast @EVENTS.trigger.scroll
            , 250
        )

    onDataSetSelected: =>
        @scope.topic.dataset = @scope.selected_dataset.id
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

    getFilteredDataSets: =>
        if (not @scope.selected_skeleton?) or (not @scope.selected_skeleton.id?)
            []
        else
            _.filter @scope.all_datasets, (e) => @scope.selected_skeleton.id in e.skeletons


angular.module('detective.controller').controller 'createTopicCtrl', CreateTopicCtrl