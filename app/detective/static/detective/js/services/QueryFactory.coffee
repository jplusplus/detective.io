angular.module('detective.service').service 'QueryFactory', [
    '$rootScope', '$stateParams', '$http',  '$location', 'TopicsFactory'
    ($rootScope, $stateParams,  $http, $location, TopicsFactory)->
        new class QueryFactory
            constructor: ->
                @query = {}
                @human_query = undefined

            updateQuery: (query)=>
                $rootScope.safeApply =>
                    @query       = query
                    @human_query = @toHumanQuery @query

            humanSearch: (query, topic)=>
                QUERY = encodeURIComponent query
                $http.get("/api/#{topic.slug}/v1/summary/human/?q=#{QUERY}")

            toHumanQuery: (query_obj=@query)=>
                return unless query_obj?
                return unless query_obj.subject?
                subject   = query_obj.subject.name    or query_obj.subject.label
                predicate = query_obj.predicate.label or query_obj.predicate.name
                object    = query_obj.object.name     or query_obj.object.label
                # i18n should be used there
                "#{subject} that #{predicate} #{object}"

            isSingleEntityQuery: (query_obj=@query)=>
                query_obj.predicate? and query_obj.predicate.name is "<<INSTANCE>>"

            isRDFQuery: (query_obj=@query)=>
                query_obj.predicate? and query_obj.object? and query_obj.object != ""

            cleanQuery: (query_obj=@query)=>
                return null unless query_obj?
                return query_obj unless query_obj.object?
                # Extract valid object's name
                # (we received an RDF formated object, with a tripplet)
                if not query_obj.object.name? and query_obj.object.subject?
                    _.extend query_obj.object,
                        name  : query_obj.object.label
                        model : query_obj.object.object
                        id    : query_obj.object.subject.name
                    delete query_obj.object.subject
                    delete query_obj.object.object
                    delete query_obj.object.label
                query_obj


            selectIndividual: (query_obj=@query, base_path)=>
                query_obj = @cleanQuery query_obj
                return if !base_path and !TopicsFactory.topic or !query_obj?
                unless base_path
                    base_path = TopicsFactory.topic.link

                if _.last(base_path) is '/'
                    base_path = base_path.substr 0, base_path.length - 1
                # Single entity selected
                if @isSingleEntityQuery(query_obj)
                    $rootScope.safeApply ->
                        $location.path "#{base_path}/#{query_obj.object.toLowerCase()}/#{query_obj.subject.name}"
                # Full RDF-formated research
                else if @isRDFQuery(query_obj)
                    # Do not pass the label
                    delete query_obj.label
                    # Create a JSON query to pass though the URL
                    query = angular.toJson query_obj
                    $rootScope.safeApply ->
                        $location.path "#{base_path}/search"
                        $location.search "q", query
    ]
