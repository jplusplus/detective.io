angular.module('detective.config').config(['$interpolateProvider',
    ($interpolateProvider)->
        # Avoid a conflict with Django Template's tags
        $interpolateProvider.startSymbol '[['
        $interpolateProvider.endSymbol   ']]'
])