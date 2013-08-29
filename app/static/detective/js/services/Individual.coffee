angular.module('detectiveServices').factory("Individual", [ '$resource', '$http', ($resource, $http)->
    $resource '/api/v1/:type/:id/', {}, {
        query: {
            method : 'GET', 
            isArray: true,
            cache  : true,
            transformResponse: $http.defaults.transformResponse.concat([(data, headersGetter) ->
                data.objects
            ])
        },
        save: {
            url:'/api/v1/:type/#',
            method : 'POST', 
            isArray: false
        }
    }
])