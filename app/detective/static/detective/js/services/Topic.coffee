angular.module('detective.service').factory("Topic", [ '$resource', '$http', ($resource, $http)->
    $resource '/api/common/v1/topic/:id/', {}, {
        get:
            method : 'GET'
            isArray: no
        put:
            method : 'PUT'
            isArray: no
        invite:
            url :'/api/common/v1/topic/:id/invite/?'
            method : 'POST'
            isArray: no
        query:
            method : 'GET'
            isArray: yes
            transformResponse: $http.defaults.transformResponse.concat([(data, headersGetter) ->
                data.objects
            ])
        cachedGet:
            method : 'GET'
            isArray: no
            cache  : yes
        cachedQuery:
            method : 'GET'
            isArray: yes
            cache  : yes
            transformResponse: $http.defaults.transformResponse.concat([(data, headersGetter) ->
                data.objects
            ])
    }
])