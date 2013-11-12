detective = angular
    .module('detective', ["detectiveServices", "detectiveFilters", "ui.bootstrap"])
    .run(
        [             
            '$rootScope', 
            '$location',
            'User'
            ($rootScope, $location, user)->
                # Location available within templates
                $rootScope.location = $location;
                $rootScope.user     = user
        ]
    )
    .config(
        [
            '$interpolateProvider',
            '$routeProvider',
            '$locationProvider'
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
                        templateUrl: "/partial/home.html"
                    })
                    .when('/404', {
                        controller: NotFoundCtrl
                        templateUrl: "/partial/404.html"
                    })
                    .when('/login', {
                        controller: UserCtrl
                        templateUrl: "/partial/login.html"
                    })
                    .when('/signup', {
                        controller: UserCtrl
                        templateUrl: "/partial/signup.html"
                    })
                    .when('/reset_password', {
                        controller: UserCtrl
                        templateUrl: "/partial/reset-password.html"  
                    })
                    .when('/reset_password_confirm', {
                        controller: UserCtrl
                        templateUrl: "/partial/reset-password-confirm.html"  
                    })
                    .when('/search', {
                        controller: IndividualSearchCtrl
                        templateUrl: "/partial/individual-list.html"
                    })  
                    # Disable common endpoints
                    .when('/common', redirectTo: '/')
                    .when('/common/contribute', redirectTo: '/')
                    .when('/:scope/contribute', {
                        controller: ContributeCtrl  
                        templateUrl: "/partial/contribute.html"
                        auth: true
                        # Resolve the Summary service before load this page
                        resolve: data: (Summary)-> Summary.get(id: "forms")
                    })
                    .when('/:scope', {
                        controller: ExploreCtrl  
                        # Allow a dynamic loading by setting the templateUrl within controller
                        template: "<div ng-include src='templateUrl'></div>"                        
                        auth: true
                    })
                    .when('/:scope/:type', {
                        controller: IndividualListCtrl  
                        templateUrl: "/partial/individual-list.html"
                        reloadOnSearch: false
                        auth: true
                        # Resolve the Summary service before load this page
                        resolve: data: (Summary)-> Summary.get(id: "forms")
                    })
                    .when('/:scope/:type/:id', {
                        controller: IndividualSingleCtrl  
                        templateUrl: "/partial/individual-single.html"  
                        reloadOnSearch: false       
                        auth: true
                        # Resolve the Summary service before load this page
                        resolve: data: (Summary)-> Summary.get(id: "forms")
                    })
                    .otherwise redirectTo: '/404'
        ]
    )

# Services module
angular.module('detectiveServices', ['ngResource', 'ngSanitize', 'ngCookies'])
