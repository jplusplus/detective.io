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