angular.module('detective').factory("Individual", [ '$resource', '$http', '$state', ($resource, $http, $state)->
    # Set default value for the common individual parameters following the
    # current state params.
    defaultsParams =
        # Use the current topic parameter as default topic
        topic:    -> $state.params.topic or "common"
        username: -> $state.params.username or "detective"
        type:     -> $state.params.type
        id:       -> $state.params.id

    # This function aims to transforms an array of relationships target ids
    # into an array of object. It ensure a seamsless transition to the new
    # structure of the relationships fields.
    #
    # For exemple, the old nodes looked like that:
    # {
    #   "id": 12,
    #   "partners": [ {id: 1}, {id: 2} ]
    # }
    #
    # The new nodes look like that (but are transform to like the old ones):
    # {
    #   "id": 12,
    #   "partners": [ 1, 2 ]
    # }
    #
    legacyRelationshipSupport = $http.defaults.transformResponse.concat([(data, headersGetter) ->
        for field, value of data
            # This legacy function only transform array fields
            if angular.isArray value
                data[field] = _.map value, (val)->
                    # Convert number value to "{id: xxxx}"
                    if angular.isNumber val then id: val else val
        data
    ])

    $resource '/api/:username/:topic/v1/:type/:id/?', defaultsParams,
        get:
            method : 'GET'
            isArray: no
            transformResponse: legacyRelationshipSupport
        query:
            method : 'GET'
            isArray: yes
            transformResponse: $http.defaults.transformResponse.concat([(data, headersGetter) ->
                data.objects
            ])
        save:
            url:'/api/:username/:topic/v1/:type/?'
            method : 'POST'
            isArray: no
            transformResponse: legacyRelationshipSupport
        bulk:
            url:'/api/:username/:topic/v1/:type/summary/bulk_upload/?'
            method : 'POST'
            isArray: no
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
        authors:
            url:'/api/:username/:topic/v1/:type/:id/authors/?'
            method: 'GET'
            isArray: yes
        relationships:
            url:'/api/:username/:topic/v1/:type/:id/relationships/:field/:target/?'
            method: 'GET'
            isArray: no
        delete:
            url:'/api/:username/:topic/v1/:type/:id/?'
            method : 'DELETE'
        update:
            url:'/api/:username/:topic/v1/:type/:id/patch/?'
            method : 'POST'
            isArray: no
            transformResponse: legacyRelationshipSupport
        createSource:
            url:'/api/:username/:topic/v1/:type/:id/patch/sources/:source_id/?'
            method : 'POST'
            isArray: no
        updateSource:
            url:'/api/:username/:topic/v1/:type/:id/patch/sources/:source_id/?'
            method : 'POST'
            isArray: no
        deleteSource:
            url:'/api/:username/:topic/v1/:type/:id/patch/sources/:source_id/?'
            method : 'DELETE'
            isArray: no
        graph:
            url:'/api/:username/:topic/v1/:type/:id/graph/?'
            method: 'GET'
            isArray: no
])