angular.module('detective.service').factory("Individual", [ '$resource', '$http', '$stateParams', ($resource, $http, $stateParams)->
    defaultsParams =
        # Use the current topic parameter as default topic
        topic: -> $stateParams.topic or "common"

    $resource '/api/:topic/v1/:type/:id/', defaultsParams,
        query:
            method : 'GET'
            isArray: yes
            transformResponse: (data)-> data.objects
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
            paramDefaults:
                topic: "common"
            transformRequest: (data, headersGetter)->
                fd = new FormData()
                # We receive an object of array
                angular.forEach data, (files, field)->
                    # Each array may contain several files
                    angular.forEach files, (file, idx)->
                        # Use idx to create a single file key
                        fd.append(field + "-" + idx, file)
                # We delete the Content-Type header (angular set it to application/json, it should be empty so the browser
                # can set it to multipart/form-data, boundary=<boundary>)
                headers = do headersGetter
                delete headers['Content-Type']

                fd
        relationships:
            url:'/api/:topic/v1/:type/:id/relationships/:field/:target/?'
            method: 'GET'
            isArray: no
        delete:
            url:'/api/:topic/v1/:type/:id/?'
            method : 'DELETE'
        update:
            url:'/api/:topic/v1/:type/:id/patch/?'
            method : 'POST'
            isArray: no
            paramDefaults:
                topic: "common"
        graph:
            url:'/api/:topic/v1/:type/:id/graph'
            method: 'GET'
            isArray: no
            paramDefaults:
                topic: "common"
                depth: "2"
])