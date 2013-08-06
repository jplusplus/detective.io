# Services
angular
    .module('detectiveServices', ['ngResource', 'ngCookies'])
    .factory("Individual", [ '$resource', '$http', ($resource, $http)->
    	$resource '/api/v1/:type/:id/#', {}, {
            query: {
                method : 'GET', 
                isArray: true,
                cache  : true,
                transformResponse: $http.defaults.transformResponse.concat([(data, headersGetter) ->
                    data.objects
                ])
            }
        }
    ])
    .factory("Search", [ '$resource', '$http', ($resource, $http)->
        $resource '/api/v1/:type/search/#', {}, {
            query: {
                method : 'GET', 
                isArray: true,
                cache  : true,
                transformResponse: $http.defaults.transformResponse.concat([(data, headersGetter) ->                    
                    data.objects
                ])
            }
        }
    ])
    .factory('User', ['$cookies', ($cookies)->      
        if $cookies.user__is_logged
            is_logged: $cookies.user__is_logged 
            username : $cookies.user__username or ''
        else
            is_logged: false 
            username : ''
    ])