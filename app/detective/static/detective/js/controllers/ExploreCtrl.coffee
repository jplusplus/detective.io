class ExploreCtrl
    # Injects dependancies
    @$inject: ['$scope', '$routeParams', 'Summary', '$location', '$timeout', '$filter', 'Page', 'topic']

    constructor: (@scope, @routeParams, @Summary, @location, @timeout, @filter, @Page, topic)->
        @scope.getTypeCount = @getTypeCount
        @Page.loading yes
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        # Current individual scope
        @scope.topic    = @routeParams.topic
        @scope.username = @routeParams.username
        # Disable loading mode
        @Page.loading no
        # Meta data about this topic
        @scope.meta = topic
        # Set page's title
        @Page.title @scope.meta.title
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
        @scope.selectedIndividual = {}
        @scope.isSearchable = (f)-> f.rules? && f.rules.is_searchable
        # ──────────────────────────────────────────────────────────────────────
        # Scope watchers
        # ──────────────────────────────────────────────────────────────────────
        @scope.$watch "selectedCountry", @selectCountry, true
        @scope.$watch "selectedIndividual", @selectIndividual, true

    # ──────────────────────────────────────────────────────────────────────────
    # Class methods
    # ──────────────────────────────────────────────────────────────────────────
    selectCountry: (val, old)=>
        @location.path "/#{@scope.username}/#{@scope.topic}/country/#{val.id}" if val.id?

    selectIndividual: (val, old)=>
        # Single entity selected
        if val.predicate? and val.predicate.name is "<<INSTANCE>>"
            @location.path "/#{@scope.username}/#{@scope.topic}/#{val.object.toLowerCase()}/#{val.subject.name}"
        # Full RDF-formated research
        else if val.predicate? and val.object? and val.object != ""
            # Do not pass the label
            delete val.label
            # Create a JSON query to pass though the URL
            query = angular.toJson val
            @location.path "/#{@scope.username}/#{@scope.topic}/search/"
            @location.search "q", query

    getTypeCount: ()=>
        return '∞' unless @scope.types?
        tt = 0
        for type in arguments
            t   = @scope.types[type]
            tt += if t? and t.count? then t.count else 0
        tt



angular.module('detective').controller 'exploreCtrl', ExploreCtrl