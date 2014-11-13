angular.module('detective.constants',  [])
angular.module('detective.controller', ['ngResource', 'ngSanitize', 'ngCookies', 'detective.constants'])
angular.module('detective.config',     ['ngProgressLite', 'ui.router', 'ui.bootstrap', 'textAngular', 'ng-embedly', 'detective.controller'])
angular.module('detective.service',    ['ngResource', 'ngSanitize', 'ngCookies', 'detective.controller'])
angular.module('detective.directive',  ['ngResource', 'ngSanitize', 'ngCookies', 'ui.router', 'detective.controller'])
angular.module('detective.filter',     ['ngResource', 'ngSanitize', 'ngCookies', 'detective.controller'])
angular.module('detective', [
    "angularFileUpload"
    'detective.constants'
    "detective.controller"
    "detective.config"
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