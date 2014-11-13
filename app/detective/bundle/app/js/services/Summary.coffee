angular.module('detective.service').factory("Summary", [ '$resource', '$http', '$stateParams', ($resource, $http, $stateParams)->
    defaultsParams =
        # Use the current topic parameter as default topic
        topic: -> $stateParams.topic or "common"
        username: -> $stateParams.username or "detective"

    $resource '/api/:username/:topic/v1/summary/:id/?', defaultsParams, {
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
            url :'/api/:username/:topic/v1/summary/export/'
    }
])