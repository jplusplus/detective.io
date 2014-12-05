class window.PageCtrl
    # Injects dependencies
    @$inject: ['$scope', '$stateParams', 'Page']

    constructor: (@scope,  @stateParams, @Page)->
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        # Build template url
        if @stateParams.slug?
            @scope.templateUrl  = "/partial/main/page/#{@stateParams.slug}/#{@stateParams.slug}.html"

angular.module('detective.controller').controller 'pageCtrl', PageCtrl