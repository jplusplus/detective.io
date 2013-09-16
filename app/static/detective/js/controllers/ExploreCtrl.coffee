class ExploreCtrl
    # Injects dependancies    
    @$inject: ['$scope', '$routeParams', 'Summary', '$location', '$timeout', '$filter', 'Page']

    constructor: (@scope, @routeParams, @Summary, @location, @timeout, @filter, @Page)->                    
        @scope.getTypeCount = @getTypeCount
        # Set page's title
        @Page.title @routeParams.scope
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
        @scope.selectedIndividual = {}
        # ──────────────────────────────────────────────────────────────────────
        # Scope watchers
        # ──────────────────────────────────────────────────────────────────────
        @scope.$watch "selectedCountry", @selectCountry, true
        @scope.$watch "selectedIndividual", @selectIndividual, true

    # ──────────────────────────────────────────────────────────────────────────
    # Class methods
    # ──────────────────────────────────────────────────────────────────────────
    selectCountry: (val, old)=> 
        @location.path "/node/country/#{val.id}" if val.id?

    selectIndividual: (val, old)=>
        @location.path "/node/#{val.model.toLowerCase()}/#{val.id}" if val.id?

    getTypeCount: ()=>
        tt = 0
        for type in arguments
            t   = @scope.types[type]
            tt += if t? and t.count? then t.count else 0
        tt

    

angular.module('detective').controller 'exploreCtrl', ExploreCtrl