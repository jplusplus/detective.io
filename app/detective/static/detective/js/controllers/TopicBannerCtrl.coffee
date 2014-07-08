class TopicBannerCtrl
    # Injects dependancies
    @$inject: ['$scope', '$routeParams']

    constructor: (@scope, @routeParams)->
        # ──────────────────────────────────────────────────────────────────────
        # Scope methods
        # ──────────────────────────────────────────────────────────────────────
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        # Get the current topic as default topic
        @scope.topic_selected = @routeParams.topic

    toggleGraphNavigation: =>
        console.log "coucou"

angular.module('detective.controller').controller 'TopicBannerCtrl', TopicBannerCtrl

# EOF
