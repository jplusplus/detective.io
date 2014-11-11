angular.module('detective.constants',  [])
angular.module('detective.controller', ['ngResource', 'ngSanitize', 'ngCookies', 'detective.constants'])
angular.module('detective.config',     ['ngProgressLite', 'ui.router', 'ui.bootstrap', 'textAngular', 'ng-embedly', 'detective.controller'])
angular.module('detective.service',    ['ngResource', 'ngSanitize', 'ngCookies', 'detective.controller'])
angular.module('detective.directive',  ['ngResource', 'ngSanitize', 'ngCookies', 'ui.router', 'detective.controller'])
angular.module('detective.filter',     ['ngResource', 'ngSanitize', 'ngCookies', 'detective.controller'])
angular.module('detective', [
    "angularFileUpload"
    "detective.config"
    "detective.controller"
    "detective.directive"
    "detective.filter"
    "detective.service"
    "monospaced.elastic"
    "ngProgressLite"
    "sun.scrollable"
    "truncate"
    "ui.bootstrap"
    'angulartics'
    'angulartics.google.analytics'
    'detective.constants'
    'ng-embedly'
    'ngAnimate'
    'ngCookies'
    'ngResource'
    'ngSanitize'
    'textAngular'
    'ui.router'
])