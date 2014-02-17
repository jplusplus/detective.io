angular.module('detective.service').factory("Summary", [ '$resource', '$http', '$routeParams', ($resource, $http, $routeParams)->
    defaultsParams =
        # Use the current topic parameter as default topic
        topic: -> $routeParams.topic or "common"

    $resource '/api/:topic/v1/summary/:id/', defaultsParams, {
        get: {
            method : 'GET',
            isArray: false
        }
    }
])