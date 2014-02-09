class SearchFormCtrl
    # Injects dependancies
    @$inject: ['$scope', '$routeParams', '$location', 'Common']

    constructor: (@scope, @routeParams, @location, @Common)->
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        @scope.selectedIndividual = {}
        @Common.query type: 'topic', (topics)=> @scope.topics = topics
        # ──────────────────────────────────────────────────────────────────────
        # Scope watchers
        # ──────────────────────────────────────────────────────────────────────
        @scope.$watch "selectedIndividual", @selectIndividual, true
        @scope.$watch (=>@routeParams), (=> @scope.topic = @routeParams.topic), yes


    selectIndividual: (val, old)=>
        # Single entity selected
        if val.predicate? and val.predicate.name is "<<INSTANCE>>"
            @location.path "/#{@scope.topic}/#{val.object.toLowerCase()}/#{val.subject.name}"
        # Full RDF-formated research
        else if val.predicate? and val.object? and val.object != ""
            # Do not pass the label
            delete val.label
            # Create a JSON query to pass though the URL
            query = angular.toJson val
            @location.path "/#{@scope.topic}/search/"
            @location.search "q", query

angular.module('detective').controller 'searchFormCtrl', SearchFormCtrl