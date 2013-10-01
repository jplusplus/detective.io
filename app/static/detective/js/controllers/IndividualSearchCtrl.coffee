class IndividualSearchCtrl extends IndividualListCtrl
    # Manage research here
    getVerbose: =>
        @scope.verbose_name = "individual"
        @scope.verbose_name_plural = "individuals"
        @Page.title @scope.verbose_name_plural          
    # Define search parameter using route's params
    getParams: =>
        id    : "rdf_search"
        limit : @scope.limit
        offset: @scope.limit * (@scope.page - 1)
        q     : @routeParams.q
        type  : "summary"

# Register the controller
angular.module('detective').controller 'individualSearchCtrl', IndividualSearchCtrl