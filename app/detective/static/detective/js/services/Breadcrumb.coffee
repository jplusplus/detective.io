angular.module('detectiveServices').factory "Breadcrumb", ["$rootScope", "$location", ($rootScope, $location) ->
    breadcrumbs = []
    breadcrumbsService = {}
    # we want to update breadcrumbs only when a route is actually changed
    # as $location.path() will get updated imediatelly (even if route change fails!)
    $rootScope.$on "$routeChangeSuccess", (event, current) ->
        pathElements = $location.path().split("/")
        result = []

        breadcrumbPath = (idx)-> "/" + pathElements.slice(0, idx + 1).join "/"
        pathElements.shift()
        
        for i in [0..pathElements.length-1]
            result.push
                name: pathElements[i]
                path: breadcrumbPath(i)


        breadcrumbs = result
        $rootScope.$broadcast 'breadcrumbRefresh'

    breadcrumbsService.getAll = -> breadcrumbs
    breadcrumbsService.getFirst = -> breadcrumbs[0] or {}
    return breadcrumbsService
]