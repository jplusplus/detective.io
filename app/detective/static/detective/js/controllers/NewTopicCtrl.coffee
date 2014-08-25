class NewTopicCtrl
    @$inject: ['$scope','$stateParams', '$state', 'User', 'TopicsFactory', 'Page']

    EVENTS:
        skeleton_selected: 'skeleton:selected'

    constructor: (@scope, @stateParams, @state, @User, @TopicsFactory, @Page)->
        @scope.skeletons = @TopicsFactory.skeletons
        @scope.selected_skeleton = {}
        @scope.new_topic = {}
        @scope.goToPlans = @goToPlans
        @scope.selectSkeleton = @selectSkeleton
        @scope.isSelected = @isSelected
        @scope.hasSelectedSkeleton = @hasSelectedSkeleton

        @Page.title "Create a new investigation"

        @scope.$on @EVENTS.skeleton_selected, @onSkeletonSelected


    goToPlans: =>
        @state.go 'tour', {scrollTo: 'pricing'}

    selectSkeleton: (skeleton)=>
        @scope.selected_skeleton = skeleton
        @scope.$broadcast @EVENTS.skeleton_selected

    isSelected: (skeleton)=>
        return false unless @scope.selected_skeleton?
        skeleton.id == @scope.selected_skeleton.id

    hasSelectedSkeleton: =>
        @scope.selected_skeleton?

    onSkeletonSelected: =>
        # if we are currently editing a new_topic
        if @scope.new_topic? and @scope.new_topic.id?
            # update on API

        # else we create it with the new skeleton and get the API result
        else
            data = topic_skeleton: @scope.selected_skeleton.id
            @TopicsFactory.post data, (data)=>
                @scope.new_topic = data


angular.module('detective.controller').controller 'newTopicCtrl', NewTopicCtrl