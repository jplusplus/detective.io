angular.module('detective.service').factory("Topic", [ '$resource', ($resource)->
    $resource '/api/detective/common/v1/topic/:id/', {}, {
        invite:
            url :'/api/detective/common/v1/topic/:id/invite/?'
            method : 'POST'
            isArray: no
        leave:
            url :'/api/detective/common/v1/topic/:id/leave/?'
            method : 'POST'
            isArray: no
        collaborators:
            url: '/api/detective/common/v1/topic/:id/collaborators/?'
            method: 'GET'
            isArray: yes
        post:
            url: '/api/detective/common/v1/topic/?'
            method: 'POST'
            isArray: no
        put:
            url: '/api/detective/common/v1/topic/:id/?'
            method: 'PUT'
        update:
            url: '/api/detective/common/v1/topic/:id/?'
            method: 'PATCH'
        cachedGet:
            method : 'GET'
            isArray: no
            cache  : yes
    }
])