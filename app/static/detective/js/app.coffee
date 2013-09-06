detective = angular
    .module('detective', ["detectiveServices", "detectiveFilters", "ui.bootstrap"])
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
            '$locationProvider',
            ($interpolateProvider, $routeProvider, $locationProvider)->
                # Avoid a conflict with Django Template's tags
                $interpolateProvider.startSymbol '[['
                $interpolateProvider.endSymbol   ']]'
                # HTML5 Mode yeah!
                $locationProvider.html5Mode true
                # Bind routes to the controllers
                $routeProvider
                    .when('/', {
                        controller: HomeCtrl
                        templateUrl: "/partial/home.html",
                    })
                    .when('/login', {
                        controller: UserCtrl
                        templateUrl: "/partial/login.html",
                    })
                    .when('/:scope', {
                        controller: ExploreCtrl  
                        # Allow a dynamic loading by setting the templateUrl within controller
                        template: "<div ng-include src='templateUrl'></div>"                        
                        auth: true
                    })
                    .when('/:scope/contribute', {
                        controller: ContributeCtrl  
                        templateUrl: "/partial/contribute.html"
                        auth: true
                    })
                    .otherwise redirectTo: '/energy'
        ]
    )

# Services module
angular.module('detectiveServices', ['ngResource', 'ngCookies'])
