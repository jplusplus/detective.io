class TopicBannerCtrl
    # Injects dependancies
    @$inject: ['$scope', '$routeParams', 'Summary']

    constructor: (@scope, @routeParams, @Summary)->
        # ──────────────────────────────────────────────────────────────────────
        # Scope methods
        # ──────────────────────────────────────────────────────────────────────
        @scope.toggleGraphNavigation = @toggleGraphNavigation
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        @scope.graphNavigationEnabled = false
        # ──────────────────────────────────────────────────────────────────────
        # Get the current topic as default topic
        @scope.topic_selected = @routeParams.topic

    toggleGraphNavigation: =>
        @scope.graphNavigationEnabled = not @scope.graphNavigationEnabled
        if @scope.graphNavigationEnabled and not @scope.graphnodes?
            @Summary.get {id: "graph", topic: @scope.topic_selected}, (data) =>
                @scope.graphnodes = data

angular.module('detective.controller').controller 'TopicBannerCtrl', TopicBannerCtrl

# EOF
