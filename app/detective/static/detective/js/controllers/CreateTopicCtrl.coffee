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

    @$inject: TopicFormCtrl.$inject.concat ['$rootScope', '$timeout', '$location', 'User', 'skeletons']

    # Note: The 4 first parameters need to stay in that order if we want the
    # `super` call to work properly (TopicFormCtrl.new.apply(this, arguments))
    constructor: (@scope, @state, @TopicsFactory, @Page, @EVENTS, @rootScope, @timeout, @location, @User, skeletons)->
        super
        @setCreatingMode()
        @scope.skeletons = skeletons
        @scope.selected_skeleton = {}
        @scope.topic = {}
        @scope.goToPlans = @goToPlans
        @scope.selectSkeleton = @selectSkeleton
        @scope.isSelected = @isSelected
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
        @scope.selected_skeleton = skeleton
        @scope.$broadcast @EVENTS.skeleton.selected

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