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
            in_topic = @isInTopic()
            in_wrong_state = @isInEmptyState() or @isInInvite() or @isInHome()
            in_topic and not in_wrong_state

    isInTopic: =>
        topic = @TopicsFactory.topic
        topic? and not _.isEmpty(topic)

    isInEmptyState: =>
        state = @state.current
        not state? or _.isEmpty(state) or _.isEmpty(state.name)

    isInInvite: =>
        @state.current.name is 'user-topic-invite'

    isInHome: =>
        ((@state.current.name or '').match(/^home/) or []).length > 0


angular.module('detective.controller').controller 'headerCtrl', HeaderCtrl