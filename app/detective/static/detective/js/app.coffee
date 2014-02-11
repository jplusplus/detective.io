angular.module('detective.service',    ['ngResource', 'ngSanitize', 'ngCookies'])
angular.module('detective.filter',     ['ngResource', 'ngSanitize', 'ngCookies'])
angular.module('detective.directive',  ['ngResource', 'ngSanitize', 'ngCookies'])
angular.module('detective.controller', ['ngResource', 'ngSanitize', 'ngCookies'])

detective = angular
    .module('detective', [
        "detective.service"
        "detective.filter"
        "detective.directive"
        "ui.bootstrap"
        "monospaced.elastic"
        "angularFileUpload"
        "ngProgressLite"
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
        ]
    )
    .config(
        [
            '$interpolateProvider',
            '$routeProvider',
            '$locationProvider'
            '$httpProvider',
            ($interpolateProvider, $routeProvider, $locationProvider, $httpProvider)->
                # Intercepts HTTP request to add cache for anonymous user
                # and to set the right csrf token from the cookies
                $httpProvider.interceptors.push('AuthHttpInterceptor');
                # Avoid a conflict with Django Template's tags
                $interpolateProvider.startSymbol '[['
                $interpolateProvider.endSymbol   ']]'
                # HTML5 Mode yeah!
                $locationProvider.html5Mode true
                # Bind routes to the controllers
                $routeProvider
                    # Disable common endpoints
                    .when('/common',                      redirectTo: '/')
                    .when('/page',                        redirectTo: '/')
                    .when('/account',                     redirectTo: '/')
                    .when('/:username/common/contribute', redirectTo: '/')
                    .when('/:username/:topic/p/',         redirectTo: '/:username/:topic/')
                    # Retrop compatibility
                    .when('/energy/',                     redirectTo: '/detective/energy/')
                    .when('/energy/:type',                redirectTo: '/detective/energy/:type')
                    .when('/energy/search',               redirectTo: '/detective/energy/search')
                    .when('/energy/:type/:id',            redirectTo: '/detective/energy/:type/:id')
                    .when('/energy/contribute',           redirectTo: '/detective/energy/contribute')
                    # Core endpoints
                    .when('/', {
                        controller: HomeCtrl
                        templateUrl: "/partial/home.html"
                    })
                    .when('/404', {
                        controller: NotFoundCtrl
                        templateUrl: "/partial/404.html"
                    })
                    # Accounts
                    .when('/account/activate', {
                        controller: UserCtrl
                        templateUrl: "/partial/account.activation.html"
                    })
                    .when('/account/reset-password', {
                        controller: UserCtrl
                        templateUrl: "/partial/account.reset-password.html"
                    })
                    .when('/account/reset-password-confirm', {
                        controller: UserCtrl
                        templateUrl: "/partial/account.reset-password.confirm.html"
                    })
                    .when('/login', {
                        controller: UserCtrl
                        templateUrl: "/partial/account.login.html"
                    })
                    .when('/signup', {
                        controller: UserCtrl
                        templateUrl: "/partial/account.signup.html"
                    })
                    .when('/contact-us', {
                        controller: ContactUsCtrl
                        templateUrl: "/partial/contact-us.html"
                    })
                    # Pages
                    .when('/page/:slug', {
                        controller: PageCtrl
                        # Allow a dynamic loading by setting the templateUrl within controller
                        template: "<div ng-include src='templateUrl'></div>"
                    })
                    # User-related url
                    .when('/:username', {
                        controller: ProfileCtrl
                        templateUrl: "/partial/account.html"
                        resolve: UserCtrl.resolve
                    })
                    # Topic-related url
                    .when('/:username/:topic/search', {
                        controller: IndividualSearchCtrl
                        templateUrl: "/partial/topic.list.html"
                        resolve: UserTopicCtrl.resolve
                    })
                    .when('/:username/:topic/p/:slug',
                        controller: ArticleCtrl
                        templateUrl: "/partial/topic.article.html"
                        resolve: UserTopicCtrl.resolve
                    )
                    .when('/:username/:topic/contribute', {
                        controller: ContributeCtrl
                        templateUrl: "/partial/topic.contribute.html"
                        resolve: UserTopicCtrl.resolve
                        auth: true
                    })
                    .when('/:username/:topic/contribute/upload', {
                        controller: BulkUploadCtrl
                        templateUrl: "/partial/topic.contribute.bulk-upload.html"
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
                        templateUrl: "/partial/topic.list.html"
                        reloadOnSearch: false
                        resolve: UserTopicCtrl.resolve
                    })
                    .when('/:username/:topic/:type/:id', {
                        controller: IndividualSingleCtrl
                        templateUrl: "/partial/topic.single.html"
                        reloadOnSearch: false
                        resolve: UserTopicCtrl.resolve
                    })
                    .otherwise redirectTo: '/404'
        ]
    )

