class window.ExploreCtrl
    # Injects dependencies
    @$inject: ['$scope', '$rootScope', '$stateParams', 'Summary', '$location', '$timeout', '$filter', 'Page', 'QueryFactory', 'topic']

    constructor: (@scope, $rootScope, @stateParams, @Summary, @location, @timeout, @filter, @Page, @QueryFactory, topic)->
        @scope.getTypeCount = @getTypeCount
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        # Current individual scope
        @scope.topic    = @stateParams.topic
        @scope.username = @stateParams.username

        # Meta data about this topic
        @scope.meta = topic
        if topic.is_uploading
            # TMP, must do something better than that
            $rootScope.$broadcast 'http:error', 'Beware, a huge data upload is in progress on this topic.'

        # Set page's title
        @Page.title @scope.meta.title
        # Build template url
        @scope.templateUrl = "/partial/main/user/topic/topic-#{@scope.username}-#{@scope.topic}.html"
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

angular.module('detective').controller 'exploreCtrl', ExploreCtrl
