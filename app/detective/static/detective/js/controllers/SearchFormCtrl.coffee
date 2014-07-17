class SearchFormCtrl
    # Injects dependancies
    @$inject: ['$scope', '$location', '$state', 'Page', 'QueryFactory', 'TopicsFactory', 'UtilsFactory']

    constructor: (@scope, @location, @state, @Page,  @QueryFactory, @TopicsFactory, @UtilsFactory)->
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        @selectedIndividual = {}
        @topics = @TopicsFactory.topics
        @topic  = @TopicsFactory.topic
        @topic_slug =  @TopicsFactory.topic.slug if @TopicsFactory.topic?
        @human_query = @QueryFactory.human_query 
        @bindHumanQuery()

        @scope.$on '$stateChangeStart', (e, current, params)=>
            @topic_slug = params.topic if params.topic?

        @scope.$on 'human_query:updated', (e, human_query)=>
            @human_query = human_query


        # Get every topics
        @TopicsFactory.getTopics (topics)=> 
            @topics = @topics.concat topics
            @TopicsFactory.topics = @topics
        # ──────────────────────────────────────────────────────────────────────
        # Scope watchers
        # ──────────────────────────────────────────────────────────────────────
        # User select an entity suggested by typeahead
        @scope.$watch (=> @selectedIndividual),=>
            @QueryFactory.selectIndividual @selectedIndividual
        , true

        # Watch location's query to update this instance of the search form
        @scope.$watch @getQuery, @QueryFactory.updateQuery, yes

        # Watch current slug and topics list to find the current topic
        @scope.$watch (=> [@topic_slug, @topics]), =>
            if @topic_slug? and @topics.length
                @topic = @getTopic @topic_slug
                @TopicsFactory.topic = @topic
        , yes

    # will init @human_query if location contains a query param, see @getQuery
    bindHumanQuery: =>
        query = @getQuery()
        if @human_query is '' and query?
            @human_query = @QueryFactory.toHumanQuery(query)

    getQuery: =>
        angular.fromJson @location.search().q

    getTopic: (slug)=>
        @TopicsFactory.getTopic slug

    isTopic: (slug)=>
        return false unless @topic?
        @topic.slug is slug

    goToTopic: =>
        # Change only if the query is empty
        if @human_query is ""
            # Update the location path
            @location.path @topic.link

    showResults: =>
        @Page.loading true
        @QueryFactory.humanSearch(@human_query, @topic).then (results)=>
            return unless results.data.objects
            objects = results.data.objects
            @Page.loading false
            if objects.length > 0
                @QueryFactory.selectIndividual objects[0], @topic.link



angular.module('detective.controller').controller 'SearchFormCtrl', SearchFormCtrl