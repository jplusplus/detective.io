class IndividualSearchCtrl extends IndividualListCtrl
    constructor:->
        super
        return @location.url("/") unless @routeParams.q?
        # Parse the JSON query
        @scope.query  = angular.fromJson @routeParams.q
        @scope.topic  = @routeParams.topic
        # Load the search syntax
        @scope.syntax = @Individual.get type: "summary", id: "syntax", topic: @scope.topic
        # Watch query change to reload the search
        @scope.search = =>
            # Extract valid object's name
            # (we received an RDF formated object, with a tripplet)
            if not @scope.query.object.name? and @scope.query.object.subject?
                _.extend(@scope.query.object,
                    name: @scope.query.object.label
                    model: @scope.query.object.object
                    id: @scope.query.object.subject.name
                )
            @location.search 'q', angular.toJson(@scope.query)
        # Custom filter to display only subject related relationship
        @scope.currentSubject = (rel)=> rel.subject? and rel.subject == @scope.query.subject.name


    # Manage research here
    getVerbose: =>
        @scope.verbose_name = "individual"
        @scope.verbose_name_plural = "individuals"
        @Page.title @scope.verbose_name_plural

    # Define search parameter using route's params
    getParams: =>
        # No query, no search
        return false unless @routeParams.q?
        id    : "rdf_search"
        limit : @scope.limit
        offset: @scope.limit * (@scope.page - 1)
        q     : @routeParams.q
        topic : @scope.topic
        type  : "summary"

# Register the controller
angular.module('detective').controller 'individualSearchCtrl', IndividualSearchCtrl