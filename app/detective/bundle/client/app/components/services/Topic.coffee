angular.module('detective').factory("Topic", [ '$resource', ($resource)->
    $resource '/api/detective/common/v1/topic/:id/?', {}, {
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
        administrators:
            url: '/api/detective/common/v1/topic/:id/administrators/?'
            method: 'GET'
            isArray: yes
        grant_admin:
            url: '/api/detective/common/v1/topic/:id/grant-admin/?'
            method: 'POST'
            isArray: no
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