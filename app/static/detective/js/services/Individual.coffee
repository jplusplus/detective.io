angular.module('detectiveServices').factory("Individual", [ '$resource', '$http', ($resource, $http)->
    $resource '/api/:topic/v1/:type/:id/', { topic: "common" }, {
        query: {
            method : 'GET',
            isArray: true,
            transformResponse: $http.defaults.transformResponse.concat([(data, headersGetter) ->
                data.objects
            ])
        },
        save: {
            url:'/api/:topic/v1/:type/?',
            method : 'POST',
            isArray: false,
            paramDefaults: {
                topic: "common"
            }
        },
        delete: {
            url:'/api/:topic/v1/:type/:id/?',
            method : 'DELETE',
        },
        update: {
            url:'/api/:topic/v1/:type/:id/patch/?',
            method : 'POST',
            isArray: false,
            paramDefaults: {
                topic: "common"
            }
        }
    }
])