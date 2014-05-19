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
        @scope.$watch =>
            @scope.userTopics
        , ( (u)=>
            @Page.loading(not u.$resolved) )
        , yes
        @scope.$watch =>
            @scope.userTopics.$resolved
        , ( (u)=>
            @Page.loading(not u) )
        , yes

        # ──────────────────────────────────────────────────────────────────────
        # Scope functions
        # ──────────────────────────────────────────────────────────────────────
        @scope.shouldShowTopics = @shouldShowTopics

    shouldShowTopics: =>
        @scope.userTopics.$resolved and @scope.userTopics.length

angular.module('detective.controller').controller 'profileCtrl', ProfileCtrl