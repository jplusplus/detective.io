class ExploreCtrl
    # Injects dependancies
    @$inject: ['$scope', '$routeParams', 'Summary', 'Individual', '$location', '$timeout', '$filter', 'Page']

    constructor: (@scope, @routeParams, @Summary, @Individual, @location, @timeout, @filter, @Page)->
        @scope.getTypeCount = @getTypeCount
        # Set page's title
        @Page.title @routeParams.topic
        @Page.loading yes
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        # Current individual scope
        @scope.topic = @routeParams.topic
        # Topic control
        @Individual.get {type: "topic", slug: @scope.topic, topic: "common" }, (data)=>
            # Disable loading mode
            @Page.loading no
            # Stop if it's an unkown topic
            return @location.path "/404" unless data.objects and data.objects.length
            # Meta data about this topic
            @scope.meta = data.objects[0]
            # Build template url
            @scope.templateUrl = "/partial/explore-#{@scope.topic}.html"
            # Countries info
            @scope.countries = @Summary.get id:"countries"
            # Types info
            @Summary.get id:"types", (d)=> @scope.types = d
            # Types info
            @Summary.get id:"forms", (d)=> @scope.forms = _.values(d)
        # Country where the user click
        @scope.selectedCountry = {}
        @scope.isSearchable = (f)-> f.rules? && f.rules.is_searchable
        # ──────────────────────────────────────────────────────────────────────
        # Scope watchers
        # ──────────────────────────────────────────────────────────────────────
        @scope.$watch "selectedCountry", @selectCountry, true

    # ──────────────────────────────────────────────────────────────────────────
    # Class methods
    # ──────────────────────────────────────────────────────────────────────────
    selectCountry: (val, old)=>
        @location.path "/#{@scope.topic}/country/#{val.id}" if val.id?

    getTypeCount: ()=>
        return '∞' unless @scope.types?
        tt = 0
        for type in arguments
            t   = @scope.types[type]
            tt += if t? and t.count? then t.count else 0
        tt



angular.module('detective').controller 'exploreCtrl', ExploreCtrl