angular.module('detective.constants',  [])
angular.module('detective.config',     ['ngProgressLite', 'ui.router', 'ui.bootstrap', 'textAngular', 'ng-embedly'])
angular.module('detective.controller', ['ngResource', 'ngSanitize', 'ngCookies'])
angular.module('detective.directive',  ['ngResource', 'ngSanitize', 'ngCookies', 'ui.router'])
angular.module('detective.filter',     ['ngResource', 'ngSanitize', 'ngCookies'])
angular.module('detective.service',    ['ngResource', 'ngSanitize', 'ngCookies'])
angular.module('detective', [
    "angularFileUpload"
    'detective.constants'
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
    'ngCookies'
    'ngResource'
    'ngSanitize'
    'ui.router'
    'textAngular'
    'angulartics',
    'angulartics.google.analytics'
    'ng-embedly'
])