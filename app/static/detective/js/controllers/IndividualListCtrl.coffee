class IndividualListCtrl
    # Injects dependancies    
    @$inject: ['$scope', '$routeParams', 'Individual', '$location', '$timeout', '$filter']

    constructor: (@scope, @routeParams, @Individual, @location, @timeout, @filter)->      
        @scope.getTypeCount = @getTypeCount
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────  
        # Read route params
        @scope.scope = @routeParams.scope
        @scope.type  = @routeParams.type
        # Get individual from database
        @scope.individual = Individual.get type: @scope.type
        # ──────────────────────────────────────────────────────────────────────
        # Scope watchers
        # ──────────────────────────────────────────────────────────────────────

    
angular.module('detective').controller 'individualListCtrl', IndividualListCtrl