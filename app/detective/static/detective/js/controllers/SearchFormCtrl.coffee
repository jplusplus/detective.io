class SearchFormCtrl
    # Injects dependencies
    @$inject: ['$scope', '$rootScope', '$location', '$state', 'Page', 'QueryFactory', 'TopicsFactory', 'UtilsFactory']

    constructor: (@scope, @rootScope, @location, @state, @Page,  @QueryFactory, @TopicsFactory, @UtilsFactory)->
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        @selectedIndividual = {}
        @topics = @TopicsFactory.topics
        @topic  = @TopicsFactory.topic
        @human_query = @QueryFactory.human_query 
        @bindHumanQuery()

        # ------------
        # Scope events
        # ------------
        @scope.$on 'human_query:updated', (e, query)=>
            @human_query = query

        # ----------------
        # Rootscope events
        # ----------------
        @rootScope.$on 'topic:updated', =>
            @topic = @TopicsFactory.topic

        # ──────────────────────────────────────────────────────────────────────
        # Scope watchers
        # ──────────────────────────────────────────────────────────────────────
        # User select an entity suggested by typeahead
        @scope.$watch (=> @selectedIndividual),=>
            @QueryFactory.selectIndividual @selectedIndividual
        , true

        # Watch location's query to update this instance of the search form
        @scope.$watch @getQuery, @QueryFactory.updateQuery, yes

    # will init @human_query if location contains a query param, see @getQuery
    bindHumanQuery: =>
        query = @getQuery()
        if @human_query is '' and query?
            @human_query = @QueryFactory.toHumanQuery(query)

    getQuery: =>
        angular.fromJson @location.search().q

    isTopic: (slug, username)=>
        return false unless @topic?
        (@topic.slug is slug) and @topic.author.username is username

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