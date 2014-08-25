class NewTopicCtrl
    @$inject: ['$scope','$stateParams', 'User', 'TopicsFactory', 'Page']
    constructor: (@scope, @stateParams, @User, @TopicsFactory, @Page)->
        @scope.skeletons = @TopicsFactory.skeletons
        @Page.title "Create a new investigation"
        console.log 'MAGIC IS MAGICAL'

angular.module('detective.controller').controller 'newTopicCtrl', NewTopicCtrl