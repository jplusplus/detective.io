angular
    .module('detective', [])
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
                        controller: LandingAllCtrl
                        templateUrl: "./partial/landing/all.html"
                    })
                    .when('/energy/', {
                        controller: LandingEnergyCtrl  
                        templateUrl: "./partial/landing/energy.html"
                    })
                    .otherwise redirectTo: '/'
        ]
    )