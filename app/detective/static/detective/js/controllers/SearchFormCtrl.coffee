class SearchFormCtrl
    # Injects dependancies
    @$inject: ['$scope', '$location', '$route', 'Page', 'QueryFactory', 'TopicsFactory', 'UtilsFactory']

    constructor: (@scope, @location, @route, @Page,  @QueryFactory, @TopicsFactory, @UtilsFactory)->
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        @selectedIndividual = {}
        @logger = @UtilsFactory.loggerDecorator('SearchFormCtrl')
        @topics = []
        @topic  = @TopicsFactory.topic
        @topic_slug = @route.current.params.topic if @route.current? and @route.current.params?
        @human_query = ''
        # Get every topics
        @TopicsFactory.getTopics (topics)=> @topics = @topics.concat topics
        # ──────────────────────────────────────────────────────────────────────
        # Scope watchers
        # ──────────────────────────────────────────────────────────────────────
        # User select an entity suggested by typeahead
        @scope.$watch (=> @selectedIndividual),=>
            @QueryFactory.selectIndividual @selectedIndividual
        , true

        # Watch location's query to update this instance of the search form
        @scope.$watch @getQuery, @QueryFactory.updateQuery, yes

        # Update the human query from this controller into the query factory
        @scope.$watch (=>@human_query), (human_query)=>
            @QueryFactory.human_query = human_query if human_query?
        , true

        # Watch current location to update the active topic
        @scope.$watch (=> @route.current), (current)=>
            return unless current? and current.params?
            @topic_slug = current.params.topic

        # Watch current slug and topics list to find the current topic
        @scope.$watch (=> [@topic_slug, @topics]), =>
            if @topic_slug? and @topics.length
                @TopicsFactory.topic = @topic = @getTopic @topic_slug
        , yes


    getQuery: =>
        angular.fromJson @location.search().q

    getTopic: (slug)=>
        @TopicsFactory.getTopic slug

    isTopic: (slug)=>
        return false unless @topic?
        @topic.slug is slug

    setTopic: (slug)=>
        @topic = @getTopic slug
        @updateLocation @topic

    updateLocation: (topic)=>
        # We are not on the selected topic
        if topic.link? and 0 isnt @location.path().indexOf topic.link
            # Update the location path
            @location.path topic.link

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