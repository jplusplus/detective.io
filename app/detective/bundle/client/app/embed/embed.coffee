angular.module('detective', [
    "ngProgressLite"
    'angulartics'
    'angulartics.google.analytics'
    'ngAnimate'
    'ngCookies'
    'ngResource'
    'ngSanitize'
    'ui.router'
    'LocalStorageModule'
]).config [
    "$urlRouterProvider", "$locationProvider",
    ($urlRouterProvider, $locationProvider)->
        # HTML5 Mode yeah!
        $locationProvider.html5Mode true
        # Not found URL
        $urlRouterProvider.otherwise("/embed/");
]