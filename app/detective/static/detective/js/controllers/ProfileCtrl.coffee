class ProfileCtrl
    # Injects dependancies
    @$inject: ['$scope', '$routeParams', 'Common', 'Page', 'user']

    constructor: (@scope,  @routeParams, @Common, @Page, user)->
        @Page.title user.username
        @Page.loading yes
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        @scope.user = user
        # Get the user's topics
        @scope.userTopics = @Common.query type: "topic", author__username: user.username
        # ──────────────────────────────────────────────────────────────────────
        # Scope watchers
        # ──────────────────────────────────────────────────────────────────────
        @scope.$watch "userTopics", ( (u)=> @Page.loading(not u.$resolved) ), yes

angular.module('detective.controller').controller 'profileCtrl', ProfileCtrl