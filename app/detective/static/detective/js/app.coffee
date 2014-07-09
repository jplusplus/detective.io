angular.module('detective.config',     ['ngProgressLite'])
angular.module('detective.controller', ['ngResource', 'ngSanitize', 'ngCookies'])
angular.module('detective.directive',  ['ngResource', 'ngSanitize', 'ngCookies'])
angular.module('detective.filter',     ['ngResource', 'ngSanitize', 'ngCookies'])
angular.module('detective.service',    ['ngResource', 'ngSanitize', 'ngCookies'])

detective = angular
    .module('detective', [
        'ui.router'
        'ngCookies'
        'ngResource'
        'ngSanitize'
        "detective.config"
        "detective.controller"
        "detective.directive"
        "detective.filter"
        "detective.service"
        "ui.bootstrap"
        "monospaced.elastic"
        "angularFileUpload"
        "ngProgressLite"
        "truncate"
        "sun.scrollable"
    ])
    .run(
        [
            '$rootScope',
            '$location',
            'User',
            'Page',
            ($rootScope, $location, user, Page)->
                # Location available within templates
                $rootScope.location  = $location;
                $rootScope.user      = user
                $rootScope.Page      = Page
                # Update global render
                $rootScope.is404     = (is404)->
                    # Value given
                    if is404?
                        # Set the 404
                        $rootScope._is404 = is404
                        # Disabled loading
                        Page.loading false if is404
                    $rootScope._is404
                $rootScope.is403 = (is403) ->
                    if is403?
                        $rootScope._is403 = is403
                        Page.loading false if is403
                    $rootScope._is403
                $rootScope.$on "$routeChangeStart", ->
                    $rootScope.is404(no)
                    $rootScope.is403 no

                # Helper checking if any 400+ error is set
                $rootScope.is40X = ->
                    $rootScope._is404 || $rootScope._is403
        ]
    )
    .config(
        [
            '$stateProvider'
            '$urlRouterProvider'
            '$interpolateProvider',
            '$locationProvider'
            '$httpProvider',
            ($stateProvider, $urlRouterProvider, $interpolateProvider, $locationProvider, $httpProvider)->
                # Intercepts HTTP request to add cache for anonymous user
                # and to set the right csrf token from the cookies
                $httpProvider.interceptors.push('AuthHttpInterceptor');
                # Avoid a conflict with Django Template's tags
                $interpolateProvider.startSymbol '[['
                $interpolateProvider.endSymbol   ']]'
                # HTML5 Mode yeah!
                $locationProvider.html5Mode true

                $urlRouterProvider.otherwise("/404");

                # ui-router configuration
                $stateProvider
                    # Core
                    .state('tour',
                        url : "/"
                        controller : HomeCtrl
                        templateUrl : '/partial/home.html'
                    )
                    .state('404',
                        url : "/404/"
                        controller : NotFoundCtrl
                        templateUrl : '/partial/404.html'
                    )
                    .state('contact-us',
                        url : "/contact-us/"
                        controller : ContactUsCtrl
                        templateUrl : '/partial/contact-us.html'
                    )
                    # Accounts
                    .state('activate',
                        url : "/account/activate/"
                        controller : UserCtrl
                        templateUrl : '/partial/account.activate.html'
                    )
                    .state('reset-password',
                        url : "/account/reset-password/"
                        controller : UserCtrl
                        templateUrl : '/partial/account.reset-password.html'
                    )
                    .state('reset-password-confirm',
                        url : "/account/reset-password-confirm/"
                        controller : UserCtrl
                        templateUrl : '/partial/account.reset-password-confirm.html'
                    )
                    .state('login',
                        url : "/login/"
                        controller : UserCtrl
                        templateUrl : '/partial/account.login.html'
                    )
                    .state('signup',
                        url : "/signup/"
                        controller : UserCtrl
                        templateUrl : '/partial/account.signup.html'
                    )
                    # Pages
                    .state('page',
                        url : "/page/:slug/"
                        controller : PageCtrl
                        # Allow a dynamic loading by setting the templateUrl within controller
                        template : "<div ng-include src='templateUrl'></div>"
                    )
                    # User-related url
                    .state('user',
                        url : "/:username/"
                        controller : ProfileCtrl
                        templateUrl : "/partial/account.html"
                        resolve : UserCtrl.resolve
                    )
                    # Topic-related url
                    .state('user-topic',
                        url : "/:username/:topic/"
                        controller : ExploreCtrl
                        # Allow a dynamic loading by setting the templateUrl within controller
                        template : "<div ng-include src='templateUrl' ng-if='templateUrl'></div>"
                    )
        ]
    )

