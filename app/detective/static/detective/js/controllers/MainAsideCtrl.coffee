class MainAsideCtrl
    @$inject: ['$scope', 'Common', 'TopicsFactory']

    constructor: (@scope, @Common, @TopicsFactory)->
    	@scope.topicsFactory = @TopicsFactory
    	# Get all featured topics
    	@Common.cachedQuery {type: 'topic', featured: 1}, (d)=> @scope.featured = d


angular.module('detective.controller').controller 'mainAsideCtrl', MainAsideCtrl