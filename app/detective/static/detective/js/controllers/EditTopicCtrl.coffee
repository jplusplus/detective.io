#=require TopicFormCtrl
class window.EditTopicCtrl extends window.TopicFormCtrl
    @$inject: TopicFormCtrl.$inject.concat ['topic']
    constructor: (@scope, @state, @TopicsFactory, @Page, @topic)->
        super
        @setEditingMode()
        @scope.topic = @topic
        @scope.saved = no
        @scope.$on 'topic:updated', =>
            @scope.saved = no
        @Page.loading false
        @Page.title "Settings of #{@topic.title}"

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

    edit: =>
        @scope.loading = yes
        @TopicsFactory.put({id: @scope.topic.id}, @scope.topic, (data)=>
                @scope.loading = no
                @scope.saved = yes
            , (response)=>
                @scope.loading = no
                @scope.save = no
                if response.status is 400
                    @scope.error = response.data.topic
        )



angular.module('detective.controller').controller 'editTopicCtrl', EditTopicCtrl