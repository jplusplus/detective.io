angular.module('detective').config(['$interpolateProvider',
    ($interpolateProvider)->
        # Avoid a conflict with Django Template's tags
        $interpolateProvider.startSymbol '[['
        $interpolateProvider.endSymbol   ']]'
])