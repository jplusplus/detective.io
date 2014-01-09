angular.module('detectiveServices').factory("Individual", [ '$resource', '$http', ($resource, $http)->
    $resource '/api/:topic/v1/:type/:id/', { topic: "common" },
        query:
            method : 'GET'
            isArray: yes
            transformResponse: $http.defaults.transformResponse.concat([(data, headersGetter) ->
                data.objects
            ])
        save:
            url:'/api/:topic/v1/:type/?'
            method : 'POST'
            isArray: no
            paramDefaults:
                topic: "common"
        bulk:
            url:'/api/:topic/v1/:type/summary/bulk_upload/?'
            method : 'POST'
            isArray: no
            headers:
                'Content-Type': no
            paramDefaults:
                topic: "common"
            transformRequest: (data)->
                fd = new FormData()
                # We receive an object of array
                angular.forEach data, (files, field)->
                    # Each array may contain several files
                    angular.forEach files, (file, idx)->
                        # Use idx to create a single file key
                        fd.append(field + "-" + idx, file)
                fd
        delete:
            url:'/api/:topic/v1/:type/:id/?'
            method : 'DELETE'
        update:
            url:'/api/:topic/v1/:type/:id/patch/?'
            method : 'POST'
            isArray: no
            paramDefaults:
                topic: "common"
])