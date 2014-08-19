# @src https://github.com/angular-ui/ui-router/wiki/Frequently-Asked-Questions#how-to-make-a-trailing-slash-optional-for-all-routes
angular.module('detective.config').config ["$urlRouterProvider", ($urlRouterProvider)->
    $urlRouterProvider.rule ($injector, $location) ->
        path = $location.path()
        # Note: misnomer. This returns a query object, not a search string
        search = $location.search()
        params = undefined
        # check to see if the path already ends in '/'
        return  if path[path.length - 1] is "/"
        # If there was no search string / query params, return with a `/`
        return path + "/"  if Object.keys(search).length is 0
        # Otherwise build the search string and return a `/?` prefix
        params = []
        angular.forEach search, (v, k) ->
            params.push k + "=" + v
            return

        path + "/?" + params.join("&")
]