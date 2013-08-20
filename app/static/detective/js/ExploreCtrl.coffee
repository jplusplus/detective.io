ExploreCtrl = ($scope, $routeParams, $rootScope, Individual, $location, $timeout)-> 
    # Current individual scope
    $scope.scope = $routeParams.scope
    # Get the list of available resources
    $scope.resources = Individual.get()
    # Individuals list, first level is the type
    $scope.individuals = { """ person: ..., organization: ... """ }
    # Current page
    $scope.page = $routeParams.page or 1


    # Load individuals from resources list
    loadResources = ->
        # Get the active resource (for the current scope)
        resources = $scope.scopeResources()
        # Resources loaded
        if resources.length
            # Get invididual
            _.each resources, (resource, i)->                                                
                $timeout(-> 
                    key    = resource.name
                    limit  = 20
                    params =
                        type  : key
                        limit : limit
                        offset: ($scope.page - 1) * limit
                    # Load the inidividual
                    $scope.individuals[key] = Individual.get params

                , i*1000)

    # Get resources list filtered by the current scope
    $scope.scopeResources = -> 
        resources = _.where $scope.resources, { scope: $scope.scope }        
            

    # True if there is a previous page
    $scope.hasPreviousPage = -> $scope.page > 1
    # True if there is a next page
    $scope.hasNextPage = ->
        has = false
        _.each $scope.individuals, (i)->              
            # Tests only loaded individuals
            if i.meta?
                has |= i.meta.next isnt null
        has
    # Go to the previous page
    $scope.previousPage = -> $location.search "page", 1*$scope.page-1
    # Go to the next page
    $scope.nextPage = -> $location.search "page", 1*$scope.page+1

    # When resources list is upadted
    $scope.$watch("resources", loadResources, true)
    # Watch the location's search to update the scope
    $scope.$on '$routeUpdate', -> 
        # Update current page
        $scope.page = $routeParams.page if $routeParams.page?
        # And load resource's individuals
        loadResources()



ExploreCtrl.$inject = ['$scope', '$routeParams', '$rootScope', 'Individual', '$location', '$timeout'];