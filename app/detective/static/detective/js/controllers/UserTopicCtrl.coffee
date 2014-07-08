class UserTopicCtrl
    # Public method to resolve
    @resolve:
        topic: ($rootScope, $state, $q, $location, Common, Page, User)->
            notFound    = ->
                deferred.reject()
                $rootScope.is404(yes)
                deferred
            forbidden = ->
                do deferred.reject
                $rootScope.is403 yes
                deferred
            deferred    = $q.defer()
            stateParams = $state.current.params
            # Checks that the current topic and user exists together
            if stateParams.topic? and stateParams.username?
                # Activate loading mode
                Page.loading yes
                # Retreive the topic for this user
                params =
                    type: "topic"
                    slug: stateParams.topic
                    author__username: stateParams.username
                Common.get params, (data)=>
                    # Stop if it's an unkown topic
                    unless data.objects and data.objects.length
                        return do (if (do User.hasReadPermission) then notFound else forbidden)
                    # Resolve the deffered result
                    deferred.resolve(data.objects[0])
            # Reject now
            else return notFound()
            # Return a deffered object
            deferred.promise

angular.module('detective.controller').controller 'userTopicCtrl', UserTopicCtrl