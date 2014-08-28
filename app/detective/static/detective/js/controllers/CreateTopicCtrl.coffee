class CreateTopicCtrl extends TopicFormCtrl
    EVENTS:
        skeleton_selected: 'skeleton:selected'

    @resolve:
        skeletons: ($state, $q, Page, TopicSkeleton)->
            console.log 'CreateTopicCtrl.resolve.skeletons !'
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

    @$inject: ['$scope', '$state', 'TopicsFactory', 'Page', 'skeletons']

    constructor: (@scope, @state, @TopicsFactory, @Page, skeletons)->
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

    create: =>
        @scope.loading = yes
        @TopicsFactory.post @scope.new_topic, (topic)=>
            @scope.loading = no


angular.module('detective.controller').controller 'createTopicCtrl', CreateTopicCtrl