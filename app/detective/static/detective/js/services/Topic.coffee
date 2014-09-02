angular.module('detective.service').factory("Topic", [ '$resource', ($resource)->
    $resource '/api/detective/common/v1/topic/:id/', {}, {
        invite:
            url :'/api/detective/common/v1/topic/:id/invite/?'
            method : 'POST'
            isArray: no
        post:
            url: '/api/detective/common/v1/topic/?'
            method: 'POST'
            isArray: no
        put:
            url: '/api/detective/common/v1/topic/:id/?'
            method: 'PUT'
        update:
            method: 'PATCH'
        cachedGet:
            method : 'GET'
            isArray: no
            cache  : yes
    }
])