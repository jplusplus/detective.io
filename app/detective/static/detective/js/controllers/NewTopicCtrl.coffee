class NewTopicCtrl
    @$inject: ['$scope','$stateParams', '$state', '$upload', 'User', 'TopicsFactory', 'Page']

    EVENTS:
        skeleton_selected: 'skeleton:selected'

    constructor: (@scope, @stateParams, @state, @upload, @User, @TopicsFactory, @Page)->
        @scope.skeletons = @TopicsFactory.skeletons
        @scope.selected_skeleton = {}
        @scope.new_topic = {}
        @scope.goToPlans = @goToPlans
        @scope.selectSkeleton = @selectSkeleton
        @scope.isSelected = @isSelected
        @scope.hasSelectedSkeleton = @hasSelectedSkeleton
        @scope.createTopic = @createTopic

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
        @scope.new_topic = @scope.new_topic or {}
        # binding to skeleton will automaticaly bind the skeleton ontolgy
        # to this new topic in API.
        @scope.new_topic.topic_skeleton = @scope.selected_skeleton.id

    createTopic: =>
        @scope.loading = yes
        @TopicsFactory.post @scope.new_topic, (topic)=>
            @scope.loading = no
            @state.go 'user-topic',
                username: topic.author.username
                topic: topic.slug


angular.module('detective.controller').controller 'newTopicCtrl', NewTopicCtrl