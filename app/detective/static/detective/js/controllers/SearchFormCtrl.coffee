class SearchFormCtrl
    # Injects dependancies
    @$inject: ['$scope', '$routeParams', '$location', 'Common', 'User']

    constructor: (@scope, @routeParams, @location, @Common, @User)->
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        @scope.selectedIndividual = {}        
        # ──────────────────────────────────────────────────────────────────────
        # Scope watchers
        # ──────────────────────────────────────────────────────────────────────
        @scope.$watch (=>@User), @fetchTopics, true
        @scope.$watch "selectedIndividual", @selectIndividual, true
        @scope.$watch (=>@routeParams), (=> @scope.topic = @routeParams.topic or @scope.topic), yes


    fetchTopics: (v,w)=>
        @Common.query type: 'topic', (topics)=> 
            # Every available topic execpt common
            @scope.topics = _.reject topics, (t)-> t.slug is "common"
            # Take the first topic as default topic
            @scope.topic = @scope.topics[0].slug unless @scope.topic            



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

angular.module('detective.controller').controller 'searchFormCtrl', SearchFormCtrl