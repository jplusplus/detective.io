class window.MainAsideCtrl
    @$inject: ['$scope', 'Common', 'TopicsFactory', '$http', 'User']

    constructor: (@scope, @Common, @TopicsFactory, @http, @User)->
        @scope.topicsFactory = @TopicsFactory
        # Get all featured topics
        @Common.cachedQuery {type: 'topic', featured: 1}, (d)=> @scope.featured = d
        # Load user investigation
        @scope.$on "user:loaded", (ev, user)=>
        	@http.get("/api/detective/common/v1/user/#{user.id}/groups/?limit=5").then (response)=>
	            # Only keep data objects
	            @scope.lasts = response.data.objects



angular.module('detective.controller').controller 'mainAsideCtrl', MainAsideCtrl