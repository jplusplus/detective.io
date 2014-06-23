class SearchFormCtrl
    # Injects dependancies
    @$inject: ['$scope',  '$routeParams', '$route',  '$location', 'QueryUtils', 'TopicsFactory', 'Common', 'Page']
    
    constructor: (@scope, @routeParams, $route, @location, @QueryUtils, @TopicsFactory, @Common, @Page)->
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        @selectedIndividual = {}

        @topics = @TopicsFactory.topics

        @scope.$watch (=> @TopicsFactory.topic), (v)=>
            @topic = v

        @TopicsFactory.getTopics (data)=>
            @topics = data
            @TopicsFactory.topics = @topics

        # ──────────────────────────────────────────────────────────────────────
        # Scope watchers
        # ──────────────────────────────────────────────────────────────────────
        @scope.$watch (=> @selectedIndividual),=>
            @QueryUtils.selectIndividual(@selectedIndividual)
        , true

        @scope.$watch @getQuery, @QueryUtils.updateQuery, yes

        @scope.$watch (=>@QueryUtils.human_query), (val)=> 
            @human_query = val
        , true

    getQuery: =>
        angular.fromJson @location.search().q

    getTopic: (slug)=> 
        @TopicsFactory.getTopic slug

    isTopic: (slug)=>
        @TopicsFactory.isTopic slug

    setTopic: (slug)=>
        @TopicsFactory.setTopic slug



angular.module('detective.controller').controller 'SearchFormCtrl', SearchFormCtrl