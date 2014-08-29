class DeleteTopicCtrl
    @$inject: ['$scope', '$state', '$timeout', 'TopicsFactory', 'Page', 'topic']

    REDIRECT_SUCCESS_TIMEOUT: 3000
    constructor: (@scope, @state, @timeout, @TopicsFactory, @Page, @topic)->
        @Page.loading no
        @scope.deleted = no
        @Page.title "Deleting #{@topic.title}"
        @scope.topic = @topic
        @scope.delete = @delete

    delete: ($form)=>
        @scope.submitted = true
        return unless $form.$valid? and $form.$valid is true
        $promise = @TopicsFactory.delete({id: @scope.topic.id}).$promise
        $promise.then @onTopicDeleted, (data)=>
            @scope.error = data

    onTopicDeleted: =>
        @scope.deleted = true
        @timeout(=>
            @state.go 'home.dashboard'
        , @REDIRECT_SUCCESS_TIMEOUT)




angular.module('detective.controller').controller 'deleteTopicCtrl', DeleteTopicCtrl