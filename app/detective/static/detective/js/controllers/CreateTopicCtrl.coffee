class CreateTopicCtrl extends TopicFormCtrl
    EVENTS:
        skeleton_selected: 'skeleton:selected'
        trigger_scroll: 'scrollTo:trigger'

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

    @$inject: ['$scope', '$state', 'TopicsFactory', 'Page', '$rootScope', '$timeout', '$location', 'skeletons']

    # Note: The 4 first parameters need to stay in that order if we want the
    # `super` call to work properly (TopicFormCtrl.new.apply(this, arguments))
    constructor: (@scope, @state, @TopicsFactory, @Page, @rootScope, @timeout, @location, skeletons)->
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

        @Page.title "Create a new investigation"
        @Page.loading no
        @scope.$on @EVENTS.skeleton_selected, @onSkeletonSelected

    # nav & scope methods
    goToPlans: =>
        @state.go 'home.tour', {scrollTo: 'pricing'}

    selectSkeleton: (skeleton)=>
        @scope.selected_skeleton = skeleton
        @scope.$broadcast @EVENTS.skeleton_selected

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
        # Angular scroll
        @location.search({scrollTo: 'topic-form'})
        @timeout(=>
                @rootScope.$broadcast @EVENTS.trigger_scroll
            , 250
        )


    create: ()=>
        @scope.loading = yes
        @TopicsFactory.post(@scope.topic, (topic)=>
            @scope.loading = no
            @state.go 'user-topic',
                username: topic.author.username
                topic: topic.slug
        , (response)=>
            @scope.loading = no
            if response.status is 400
                @scope.error = response.data.topic
        )


angular.module('detective.controller').controller 'createTopicCtrl', CreateTopicCtrl