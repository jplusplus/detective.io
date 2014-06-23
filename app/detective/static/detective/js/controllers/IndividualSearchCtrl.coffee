class IndividualSearchCtrl extends IndividualListCtrl
    @$inject: IndividualListCtrl.$inject.concat ['QueryUtils', 'TopicsFactory']

    constructor:->
        super
        dep_number     = IndividualListCtrl.$inject.length
        @queryUtils    = arguments[dep_number]
        @TopicsFactory = arguments[dep_number + 1] 
        @topic         = @TopicsFactory.topic

        # Custom filter to display only subject related relationship
        @scope.currentSubject = @currentSubject

        return @location.url("/") unless @routeParams.q?
        # Parse the JSON query
        @scope.query  = @queryUtils.query
        # Load the search syntax
        @Individual.get {type: "summary", id: "syntax"}, (d)=>
            @scope.syntax = d
            # Merge the two predicates array
            @scope.syntax.predicates = d.predicate.literal.concat( d.predicate.relationship )
        # Watch query change to reload the search
        @scope.search = @search

    search: =>
        @queryUtils.selectIndividual(@scope.query, @topic.link)

    currentSubject: (rel)=> rel.subject? and rel.subject == @scope.query.subject.name

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
        type  : "summary"

    requestCsvExport: (cb) =>
        @Summary.export { q : angular.toJson @scope.query }, cb

# Register the controller
angular.module('detective.controller').controller 'individualSearchCtrl', IndividualSearchCtrl