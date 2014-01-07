detective = angular
    .module('detective', ["detectiveServices", "detectiveFilters", "ui.bootstrap", "monospaced.elastic"])
    .run(
        [
            '$rootScope',
            '$location',
            'User',
            'Page',
            ($rootScope, $location, user, Page)->
                # Location available within templates
                $rootScope.location = $location;
                $rootScope.user     = user
                $rootScope.Page     = Page
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
                    .when('/account/activate', {
                        controller: UserCtrl
                        templateUrl: "/partial/account-activation.html"
                    })
                    .when('/account/reset-password', {
                        controller: UserCtrl
                        templateUrl: "/partial/reset-password.html"
                    })
                    .when('/account/reset-password-confirm', {
                        controller: UserCtrl
                        templateUrl: "/partial/reset-password-confirm.html"
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
                     .when('/bulk_upload', {
                        controller: BulkUploadCtrl
                        templateUrl: "/partial/bulk_upload.html"
                    })
                    .when('/search', {
                        controller: IndividualSearchCtrl
                        templateUrl: "/partial/individual-list.html"
                    })
                    .when('/contact-us', {
                        controller: ContactUsCtrl
                        templateUrl: "/partial/contact-us.html"
                    })
                    .when('/page/:slug', {
                        controller: PageCtrl
                        # Allow a dynamic loading by setting the templateUrl within controller
                        template: "<div ng-include src='templateUrl'></div>"
                    })
                    # Disable common endpoints
                    .when('/common',  redirectTo: '/')
                    .when('/page',    redirectTo: '/')
                    .when('/account', redirectTo: '/')
                    .when('/common/contribute', redirectTo: '/')
                    .when('/:topic/contribute', {
                        controller: ContributeCtrl
                        templateUrl: "/partial/contribute.html"
                        auth: true
                    })
                    .when('/:topic', {
                        controller: ExploreCtrl
                        # Allow a dynamic loading by setting the templateUrl within controller
                        template: "<div ng-include src='templateUrl' ng-if='templateUrl'></div>"
                    })
                    .when('/:topic/:type', {
                        controller: IndividualListCtrl
                        templateUrl: "/partial/individual-list.html"
                        reloadOnSearch: false
                    })
                    .when('/:topic/:type/:id', {
                        controller: IndividualSingleCtrl
                        templateUrl: "/partial/individual-single.html"
                        reloadOnSearch: false
                    })
                    .otherwise redirectTo: '/404'
        ]
    )

# Services module
angular.module('detectiveServices', ['ngResource', 'ngSanitize', 'ngCookies'])
