#=require TopicFormCtrl
class window.EditTopicCtrl extends window.TopicFormCtrl
    @$inject: TopicFormCtrl.$inject.concat ['$rootScope', 'topic']
    constructor: (@scope, @state, @TopicsFactory, @Page, @EVENTS, @rootScope, @topic)->
        super
        @setEditingMode()
        @scope.topic = @topic
        @scope.saved = no
        @scope.deleteTopicBackground = @deleteTopicBackground
        @scope.$on @EVENTS.topic.user_updated, =>
            @scope.saved = no

        @scope.$on @EVENTS.topic.updated, (e, topic)=>
            @topic = topic
            @scope.topic = @topic

        @Page.loading false
        @Page.title "Settings of #{@topic.title}"

    deleteTopicBackground: =>
        @topic.background = null

    edit: =>
        @scope.loading = yes
        @TopicsFactory.put({id: @scope.topic.id}, @scope.topic, (data)=>
                @scope.$broadcast @EVENTS.topic.updated, data
                @scope.loading = no
                @scope.saved = yes
            , (response)=>
                @scope.loading = no
                @scope.save = no
                if response.status is 400
                    @scope.error = response.data.topic
        )



angular.module('detective.controller').controller 'editTopicCtrl', EditTopicCtrl