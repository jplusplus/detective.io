class PageCtrl
    # Injects dependancies
    @$inject: ['$scope', '$routeParams', 'Page']

    constructor: (@scope,  @routeParams, @Page)->
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        # Build template url
        if @routeParams.slug?
            @scope.templateUrl  = "/partial/page-#{@routeParams.slug}.html"

angular.module('detective').controller 'pageCtrl', PageCtrl