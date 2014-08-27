class CreateTopicCtrl extends TopicFormCtrl
    EVENTS:
        skeleton_selected: 'skeleton:selected'

    constructor: (@scope, @state, @TopicsFactory, @Page)->
        super
        @setCreatingMode()
        @scope.skeletons = @TopicsFactory.skeletons
        @scope.selected_skeleton = {}
        @scope.topic = {}
        @scope.goToPlans = @goToPlans
        @scope.selectSkeleton = @selectSkeleton
        @scope.isSelected = @isSelected
        @scope.hasSelectedSkeleton = @hasSelectedSkeleton
        @scope.shouldShowForm = @hasSelectedSkeleton

        @Page.title "Create a new investigation"

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