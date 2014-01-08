angular.module('detectiveServices').factory("Common", [ '$resource', '$http', ($resource, $http)->
    $resource '/api/common/v1/:type/:id/', {}, {
        get:
            method : 'GET'
            isArray: false
            cache  : true
        query:
            method : 'GET'
            isArray: true
            transformResponse: $http.defaults.transformResponse.concat([(data, headersGetter) ->
                data.objects
            ])
    }
])