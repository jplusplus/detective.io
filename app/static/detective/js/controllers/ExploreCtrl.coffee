class ExploreCtrl
    # Injects dependancies    
    @$inject: ['$scope', '$routeParams', 'Individual', '$location', '$timeout', '$filter']

    constructor: (@scope, @routeParams, @Individual, @location, @timeout, @filter)->      
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────  
        # Current individual scope
        @scope.scope = @routeParams.scope
        # Build template url
        @scope.templateUrl = "/partial/explore-#{@scope.scope}.html"

        # ──────────────────────────────────────────────────────────────────────
        # Scope watchers
        # ──────────────────────────────────────────────────────────────────────


    # ──────────────────────────────────────────────────────────────────────────
    # Class methods
    # ──────────────────────────────────────────────────────────────────────────
    

angular.module('detective').controller 'exploreCtrl', ExploreCtrl