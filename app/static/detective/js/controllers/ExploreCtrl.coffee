class ExploreCtrl
    # Injects dependancies    
    @$inject: ['$scope', '$routeParams', 'Summary', '$location', '$timeout', '$filter']

    constructor: (@scope, @routeParams, @Summary, @location, @timeout, @filter)->      
        @scope.getTypeCount = @getTypeCount
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────  
        # Current individual scope
        @scope.scope           = @routeParams.scope
        # Build template url
        @scope.templateUrl     = "/partial/explore-#{@scope.scope}.html"
        # Countries info
        @scope.countries       = @Summary.get id:"countries"
        # Types info
        @scope.types           = @Summary.get id:"types" 
        # Country where the user click
        @scope.selectedCountry = {}
        # ──────────────────────────────────────────────────────────────────────
        # Scope watchers
        # ──────────────────────────────────────────────────────────────────────
        @scope.$watch "selectedCountry", @selectCountry, true

    # ──────────────────────────────────────────────────────────────────────────
    # Class methods
    # ──────────────────────────────────────────────────────────────────────────
    selectCountry: (val, old)=> 
        @location.path "#{@routeParams.scope}/explore/country/#{val.id}" if val.id?


    getTypeCount: ()=>
        tt = 0
        for type in arguments
            t   = _.findWhere(@scope.types, name: type)
            tt += if t? and t.count? then t.count else 0
        tt

    

angular.module('detective').controller 'exploreCtrl', ExploreCtrl