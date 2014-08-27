class DeleteTopicCtrl
    @$inject: ['$scope', 'TopicsFactory', 'topic']
    constructor: (@scope, @TopicsFactory, @topic)->
        @scope.topic = @topic

    delete: ($form)=>
        @scope.submitted = true
        return unless $form.$valid? and $form.$valid is true


angular.module('detective.controller').controller 'deleteTopicCtrl', DeleteTopicCtrl