detective = angular
    .module('detective', ["ui.bootstrap", "detectiveServices", "detectiveFilters"])
    .run(
        [             
            '$rootScope', 
            '$location',
            ($rootScope, $location)->
                # Location available within templates
                $rootScope.location = $location;
        ]
    )
    .config(
        [
            '$interpolateProvider', 
            '$routeProvider', 
            ($interpolateProvider, $routeProvider)->
                # Avoid a conflict with Django Template's tags
                $interpolateProvider.startSymbol '[['
                $interpolateProvider.endSymbol   ']]'
                # Bind routes to the controllers
                $routeProvider
                    .when('/', {
                        controller: HomeCtrl
                        templateUrl: "./partial/landing/all.html",
                    })
                    .when('/login', {
                        controller: UserCtrl
                        templateUrl: "./partial/login.html",
                    })
                    .when('/:scope/contribute', {
                        controller: ContributeCtrl  
                        templateUrl: "./partial/contribute.html"
                        auth: true
                    })
                    .when('/:scope/explore', {
                        controller: ExploreCtrl  
                        templateUrl: "./partial/explore.html"
                        reloadOnSearch: false
                        auth: true
                    })
                    .otherwise redirectTo: '/energy/contribute'
        ]
    )

# Services module
angular.module('detectiveServices', ['ngResource', 'ngCookies'])
