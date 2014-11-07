class window.MainAsideCtrl
    @$inject: ['$scope', 'Common', 'TopicsFactory', '$http', 'User', 'Group']

    constructor: (@scope, @Common, @TopicsFactory, @http, @User, @Group)->
        @scope.topicsFactory = @TopicsFactory
        @scope.userLoaded = false
        # Get all featured topics
        @Common.cachedQuery {type: 'topic', featured: 1}, (d)=> @scope.featured = d



angular.module('detective.controller').controller 'mainAsideCtrl', MainAsideCtrl