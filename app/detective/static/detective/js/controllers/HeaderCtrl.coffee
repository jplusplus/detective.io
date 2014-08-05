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

        @scope.shouldShowAddEntity = =>
            return false unless @isInTopic()
            return @scope.user.hasAddPermission(@TopicsFactory.topic.ontology_as_mod)

        @scope.shouldShowTopicSearch = =>
            return false unless @isInTopic()
            return false if @isInInvite()
            true

    isInTopic: =>
        topic = @TopicsFactory.topic
        topic? and not _.isEmpty(topic)

    isInInvite: =>
        @state.current.name == 'user-topic-invite'


angular.module('detective.controller').controller 'headerCtrl', HeaderCtrl