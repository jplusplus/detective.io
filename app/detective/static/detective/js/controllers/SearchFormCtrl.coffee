class SearchFormCtrl
    # Injects dependancies
    @$inject: ['$scope', '$location', '$route', 'QueryUtils', 'TopicsFactory', 'UtilsFactory']
    
    constructor: (@scope, @location, @route,  @QueryUtils, @TopicsFactory, @UtilsFactory)->
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        @selectedIndividual = {}
        @logger = @UtilsFactory.loggerDecorator('SearchFormCtrl')
        @topics = @TopicsFactory.topics
        @topic  = @TopicsFactory.current

        @topic_slug = @route.current.params.topic if @route.current? and @route.current.params? 


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

        @scope.$watch (=> @route.current), (current)=>
            return unless current? and current.params?
            @topic_slug = current.params.topic

        @scope.$watch (=> @topic_slug + @topics), =>
            @topic = @getTopic @topic_slug
            @TopicsFactory.topic = @topic
        
        # we get all topics here
        @TopicsFactory.getTopics (data)=>
            @topics = data
            @TopicsFactory.topics = @topics

    getQuery: =>
        angular.fromJson @location.search().q

    getTopic: (slug)=> 
        @TopicsFactory.getTopic slug

    isTopic: (slug)=>
        return false unless @topic?
        @topic.slug is slug

    setTopic: (slug)=>
        @topic = @getTopic slug



angular.module('detective.controller').controller 'SearchFormCtrl', SearchFormCtrl