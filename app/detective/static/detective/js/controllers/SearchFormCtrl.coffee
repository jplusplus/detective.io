class SearchFormCtrl
    # Injects dependancies
    @$inject: ['$scope', '$location', '$route', 'Page', 'QueryFactory', 'TopicsFactory', 'UtilsFactory']
    
    constructor: (@scope, @location, @route, @Page,  @QueryFactory, @TopicsFactory, @UtilsFactory)->
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        @selectedIndividual = {}
        @logger = @UtilsFactory.loggerDecorator('SearchFormCtrl')
        @topics = @TopicsFactory.topics
        @topic  = @TopicsFactory.current
        @scope.human_query = ''

        @topic_slug = @route.current.params.topic if @route.current? and @route.current.params? 


        # ──────────────────────────────────────────────────────────────────────
        # Scope watchers
        # ──────────────────────────────────────────────────────────────────────
        @scope.$watch (=> @selectedIndividual),=>
            @QueryFactory.selectIndividual(@selectedIndividual)
        , true

        @scope.$watch @getQuery, @QueryFactory.updateQuery, yes

        @scope.$watch (=>@human_query), (val)=>
            @QueryFactory.human_query = @human_query
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

    showResults: =>
        @Page.loading true
        # @logger.log 'showResults', "@human_query", @human_query
        @QueryFactory.humanSearch(@human_query, @topic).then (results)=>
            return unless results.data.objects
            objects = results.data.objects
            @Page.loading false
            if objects.length > 0 
                @QueryFactory.selectIndividual objects[0], @topic.link



angular.module('detective.controller').controller 'SearchFormCtrl', SearchFormCtrl