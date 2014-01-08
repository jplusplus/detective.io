angular.module('detectiveServices').factory("Summary", [ '$resource', '$http', ($resource, $http)->
    $resource '/api/:topic/v1/summary/:id/', { topic: "common" }, {
        get: {
            method : 'GET',
            isArray: false,
            cache  : true
        }
    }
])