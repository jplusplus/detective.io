class window.MainAsideCtrl
    @$inject: ['$scope', 'Common', 'TopicsFactory', '$http', 'User', 'Group']

    constructor: (@scope, @Common, @TopicsFactory, @http, @User, @Group)->
        @scope.topicsFactory = @TopicsFactory
        @scope.userLoaded = false
        # Get all featured topics
        @Common.cachedQuery {type: 'topic', featured: 1}, (d)=> @scope.featured = d
        # Load user investigation
        @scope.$on "user:loaded", (ev, user)=>
            if not @scope.userLoaded
                @scope.userLoaded = true
                (@Group.collaborator { user_id : user.id }).$promise.then (data) =>
                    # Only keep data objects
                    @scope.lasts = data.objects



angular.module('detective.controller').controller 'mainAsideCtrl', MainAsideCtrl