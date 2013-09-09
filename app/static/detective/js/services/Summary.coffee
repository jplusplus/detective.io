angular.module('detectiveServices').factory("Summary", [ '$resource', ($resource)->
    $resource '/api/v1/summary/:id/', {}, {
        get: {
            method : 'GET', 
            isArray: true,
            cache  : true
        }
    }
])