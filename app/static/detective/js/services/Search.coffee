angular.module('detectiveServices').factory("Search", [ '$resource', '$http', ($resource, $http)->
    $resource '/api/:scope/v1/:type/search/#', {}, {
        query: {
            method : 'GET', 
            isArray: true,
            transformResponse: $http.defaults.transformResponse.concat([(data, headersGetter) ->                    
                data.objects
            ])
        }
    }
])