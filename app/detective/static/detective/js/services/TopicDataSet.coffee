angular.module('detective.service').factory("TopicDataSet", [
    '$resource'
    '$http'
    ($resource, $http)->
        $resource '/api/detective/common/v1/topicdataset/', {}, {
            get:
                method : 'GET'
                isArray: yes
                transformResponse: $http.defaults.transformResponse.concat([(data, headersGetter) ->
                    _.map data.objects, (e) ->
                        e.skeletons = _.pluck e.skeletons, 'id'
                        e
                ])
            cachedGet:
                method : 'GET'
                isArray: yes
                transformResponse: $http.defaults.transformResponse.concat([(data, headersGetter) ->
                    _.map data.objects, (e) ->
                        e.skeletons = _.pluck e.skeletons, 'id'
                        e
                ])
                cache  : yes
        }
])