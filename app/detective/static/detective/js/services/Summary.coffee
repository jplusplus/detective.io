angular.module('detective.service').factory("Summary", [ '$resource', '$http', '$stateParams', ($resource, $http, $stateParams)->
    defaultsParams =
        # Use the current topic parameter as default topic
        topic: -> $stateParams.topic or "common"

    $resource '/api/:topic/v1/summary/:id/', defaultsParams, {
        get:
            method : 'GET'
            isArray: false
        cachedGet:
            method : 'GET'
            isArray: false
            cache  : yes
        export:
            isArray : false
            cache  : no
            method : 'GET'
            url :'/api/:topic/v1/summary/export/'
    }
])