#=require TopicFormCtrl
class window.EditTopicCtrl extends window.TopicFormCtrl
    @$inject: TopicFormCtrl.$inject.concat ['$rootScope', 'topic']
    constructor: (@scope, @state, @TopicsFactory, @Page, @EVENTS, @rootScope, @topic)->
        super
        @setEditingMode()
        @master = angular.copy @topic
        @scope.topic = @topic
        @scope.saved = no
        @scope.deleteTopicBackground = @deleteTopicBackground
        @scope.$on @EVENTS.topic.user_updated, =>
            @scope.saved = no

        @scope.$on @EVENTS.topic.updated, (e, topic)=>
            @topic = topic
            @scope.topic = @topic
            # avoid reference binding, otherwise @topicChanges will return an
            # empty object everytime.
            @master = angular.copy @topic

        @Page.loading false
        @Page.title "Settings of #{@topic.title}"

    deleteTopicBackground: =>
        @topic.background = null

    topicChanges: (topic)=>
        clean = (val)->
            val = angular.copy val
            if val == "" or val == undefined
                # Empty input must be null
                val = null
            val
        now = topic
        prev = @master
        changes = {}
        for prop of now
            now_val  = clean now[prop]
            prev_val = clean prev[prop]
            if typeof now_val isnt "function" and prop.indexOf("$") != 0
                unless angular.equals prev_val, now_val
                    changes[prop] = now_val
        changes

    edit: =>
        @scope.loading = yes
        changes = @topicChanges @scope.topic

        @TopicsFactory.update({id: @scope.topic.id}, changes, (data)=>
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