###
# @requires IndividualListCtrl.js
###
class window.IndividualSearchCtrl extends window.IndividualListCtrl
    @$inject: IndividualListCtrl.$inject.concat ['QueryFactory', 'TopicsFactory']

    constructor:->
        super
        dep_number     = IndividualListCtrl.$inject.length
        @QueryFactory  = arguments[dep_number]
        @TopicsFactory = arguments[dep_number + 1]

        # Custom filter to display only subject related relationship
        @scope.currentSubject = @currentSubject

        unless @stateParams.q?
            return @state.go("user-topic", {username: @stateParams.username, topic: @stateParams.topic} )

        # Parse the JSON query
        @scope.query  = @QueryFactory.query

        # Load the search syntax
        @Individual.get {type: "summary", id: "syntax"}, (d)=>
            @scope.syntax = d
            # Merge the two predicates array
            @scope.syntax.predicates = _.map (_.groupBy (d.predicate.literal.concat d.predicate.relationship), 'name'), (a) => a[0]
       # Watch query change to reload the search
        @scope.search = @search

    search: =>
        query = @QueryFactory.query

        # we recreate query
        if query.predicate
            predicate = _.findWhere @scope.syntax.predicates, name: query.predicate.name
            query.predicate = predicate

        @QueryFactory.selectIndividual(query, @TopicsFactory.topic.link)
        @QueryFactory.updateQuery query

    currentSubject: (rel)=> rel.subject? and rel.subject == @scope.query.subject.name

    # Manage research here
    getVerbose: =>
        @scope.verbose_name = "Entity for this query"
        @scope.verbose_name_plural = "Entities for this query"
        @Page.title @scope.verbose_name_plural

    # Define search parameter using route's params
    getParams: =>
        # No query, no search
        return false unless @stateParams.q?
        id    : "rdf_search"
        limit : @scope.limit
        offset: @scope.limit * (@scope.page - 1)
        q     : @QueryFactory.query
        type  : "summary"

    requestCsvExport: (cb) =>
        @Summary.export { q : angular.toJson @scope.query }, cb

# Register the controller
angular.module('detective').controller 'individualSearchCtrl', IndividualSearchCtrl