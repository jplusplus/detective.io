detective = angular
    .module('detective', ["detectiveServices"])
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
                        templateUrl: "./partial/landing/all.html",
                    })
                    .when('/login', {
                        controller: UserCtrl
                        templateUrl: "./partial/login.html",
                    })
                    .when('/:topic/contribute', {
                        controller: ContributeCtrl  
                        templateUrl: "./partial/contribute.html"
                        auth: true
                    })
                    .otherwise redirectTo: '/'
        ]
    )