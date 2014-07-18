class ExploreCtrl
    # Injects dependancies
    @$inject: ['$scope', '$stateParams', 'Summary', '$location', '$timeout', '$filter', 'Page', 'QueryFactory', 'topic']

    constructor: (@scope, @stateParams, @Summary, @location, @timeout, @filter, @Page, @QueryFactory, topic)->
        @scope.getTypeCount = @getTypeCount
        @Page.loading no
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        # Current individual scope
        @scope.topic    = @stateParams.topic
        @scope.username = @stateParams.username

        # Meta data about this topic
        @scope.meta = topic

        # Set page's title
        @Page.title @scope.meta.title
        # Build template url
        @scope.templateUrl = "/partial/topic.explore-#{@scope.topic}.html"
        # Countries info
        @scope.countries = @Summary.get id:"countries"
        # Types info
        @Summary.get id:"types", (d)=> @scope.types = d
        # Types info
        @Summary.get id:"forms", (d)=> @scope.forms = _.values(d)
        # Country where the user click
        @scope.selectedCountry = {}
        @scope.isSearchable = (f)-> f.rules? && f.rules.is_searchable
        @scope.shouldDisplayMap = => _.findWhere(@scope.meta.models, name: 'Country')?
        # .csv export
        @scope.csvExport = @csvExport
        # ──────────────────────────────────────────────────────────────────────
        # Scope watchers
        # ──────────────────────────────────────────────────────────────────────
        @scope.$watch "selectedCountry", @selectCountry, true

    # ──────────────────────────────────────────────────────────────────────────
    # Class methods
    # ──────────────────────────────────────────────────────────────────────────
    selectCountry: (val, old)=>
        @location.path "/#{@scope.username}/#{@scope.topic}/country/#{val.id}" if val.id?

    getTypeCount: ()=>
        return '∞' unless @scope.types?
        tt = 0
        for type in arguments
            t   = @scope.types[type]
            tt += if t? and t.count? then t.count else 0
        tt

    csvExport: =>
        @Summary.export {}, (d) ->
            file = new Blob([d.data], { type : 'application/zip' })
            saveAs(file, d.filename)

angular.module('detective.controller').controller 'exploreCtrl', ExploreCtrl
