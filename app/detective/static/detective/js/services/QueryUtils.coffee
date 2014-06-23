angular.module('detective.service').service 'QueryUtils', [
    '$rootScope', '$routeParams', '$location', 'TopicsFactory'
    ($rootScope, $routeParams, $location, TopicsFactory)->
        new class QueryUtils
            constructor: ->
                @query = {}
                @human_query = undefined

            updateQuery: (query)=>
                $rootScope.safeApply =>
                    @query       = query
                    @human_query = @toHumanQuery @query

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
                unless query_obj.object?
                    return query_obj
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
                return if !base_path and !TopicsFactory.topic
                query_obj = @cleanQuery query_obj
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
