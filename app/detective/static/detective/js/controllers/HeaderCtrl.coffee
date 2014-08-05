class HeaderCtrl
    @$inject: ['$scope', '$state', 'Common', 'TopicsFactory', '$location']

    constructor: (@scope, @state, @Common, @TopicsFactory, @location)->
        # Watch current topic
        @scope.$watch (=>@TopicsFactory.topic), (topic)=> @scope.topic = topic
        # Watch URL change to determine the login destination
        @scope.$watch (=>@location.url()), (url)=>
            @scope.nextLogin = url if url isnt "/login"

        @scope.loginParams = =>
            nextState: @state.current.name
            nextParams: angular.toJson(@state.params)

        @scope.showAddEntity = =>
            topic = @TopicsFactory.topic
            in_topic = topic? and not _.isEmpty(topic)
            if not in_topic
                return false
            else
                return @scope.user.hasAddPermission(topic.ontology_as_mod)


angular.module('detective.controller').controller 'headerCtrl', HeaderCtrl