class UserTopicCtrl
    # Public method to resolve
    @resolve:
        topic: ($rootScope, $route, $q, $location, Common)->
            notFound    = ->
                deferred.reject()
                $rootScope.is404(yes)
                deferred
            deferred    = $q.defer()
            routeParams = $route.current.params
            # Checks that the current topic and user exists together
            if routeParams.topic? and routeParams.username?
                # Retreive the topic for this user
                params =
                    type: "topic"
                    slug: routeParams.topic
                    author__username: routeParams.username
                Common.get params, (data)=>
                    # Stop if it's an unkown topic
                    return notFound() unless data.objects and data.objects.length
                    # Resolve the deffered result
                    deferred.resolve(data.objects[0])
            # Reject now
            else return notFound()
            # Return a deffered object
            deferred.promise

angular.module('detective.controller').controller 'userTopicCtrl', UserTopicCtrl