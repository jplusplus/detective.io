detective = angular
    .module('detective', ["detectiveServices", "detectiveFilters", "ui.bootstrap", "monospaced.elastic", "angularFileUpload", "ngProgressLite"])
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

                    # Retrop compatibility
                    .when('/energy/',           redirectTo: '/detective/energy/')
                    .when('/energy/:type',      redirectTo: '/detective/energy/:type')
                    .when('/energy/search',     redirectTo: '/detective/energy/search')
                    .when('/energy/:type/:id',  redirectTo: '/detective/energy/:type/:id')
                    .when('/energy/contribute', redirectTo: '/detective/energy/contribute')
                    # Disable endpoint
                    .when('/:username/common/contribute', redirectTo: '/')
                    .when('/:username/:topic/p/', redirectTo: '/:username/:topic/')
                    # User-related url
                    .when('/:username', {
                        controller: ProfileCtrl
                        templateUrl: "/partial/profile.html"
                        resolve: UserCtrl.resolve
                    })
                    # Topic-related url
                    .when('/:username/:topic/search', {
                        controller: IndividualSearchCtrl
                        templateUrl: "/partial/individual-list.html"
                        resolve: UserTopicCtrl.resolve
                    })
                    .when('/:username/:topic/p/:slug',
                        controller: ArticleCtrl
                        templateUrl: "/partial/article.html"
                        resolve: UserTopicCtrl.resolve
                    )
                    .when('/:username/:topic/contribute', {
                        controller: ContributeCtrl
                        templateUrl: "/partial/contribute.html"
                        resolve: UserTopicCtrl.resolve
                        auth: true
                    })
                    .when('/:username/:topic/contribute/upload', {
                        controller: BulkUploadCtrl
                        templateUrl: "/partial/bulk-upload.html"
                        resolve: UserTopicCtrl.resolve
                        auth: true
                    })
                    .when('/:username/:topic', {
                        controller: ExploreCtrl
                        # Allow a dynamic loading by setting the templateUrl within controller
                        template: "<div ng-include src='templateUrl' ng-if='templateUrl'></div>"
                        resolve: UserTopicCtrl.resolve
                    })
                    .when('/:username/:topic/:type', {
                        controller: IndividualListCtrl
                        templateUrl: "/partial/individual-list.html"
                        reloadOnSearch: false
                        resolve: UserTopicCtrl.resolve
                    })
                    .when('/:username/:topic/:type/:id', {
                        controller: IndividualSingleCtrl
                        templateUrl: "/partial/individual-single.html"
                        reloadOnSearch: false
                        resolve: UserTopicCtrl.resolve
                    })
                    .otherwise redirectTo: '/404'
        ]
    )

# Services module
angular.module('detectiveServices', ['ngResource', 'ngSanitize', 'ngCookies'])
