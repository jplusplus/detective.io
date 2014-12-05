class LeaveTopicModalCtrl
    @$inject: ['$scope', '$modalInstance', 'TopicsFactory', 'topic']
    constructor: (@scope, @modalInstance, @TopicsFactory, @topic)->
        @quitted = false
        @loading = false

    close: (result=@quitted)=>
        @modalInstance.close(result)

    leave: ()=>
        @loading = true
        params =
            id: @topic.id
        @TopicsFactory.leave(params, undefined, =>
            @loading = false
            @quitted = true
        )

angular.module('detective').controller 'leaveTopicModalCtrl', LeaveTopicModalCtrl