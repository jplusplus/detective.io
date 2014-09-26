class window.HeaderCtrl
    @$inject: ['$scope', '$state', 'Common', 'User', 'TopicsFactory', '$location']

    constructor: (@scope, @state, @Common, User, @TopicsFactory, @location)->
        @scope.user = User
        @scope.userMenuOpened = false
        # Watch current topic
        @scope.$watch (=>@TopicsFactory.topic), (topic)=> @scope.topic = topic
        # Watch URL change to determine the login destination
        @scope.$watch (=>@location.url()), (url)=>
            @scope.nextLogin = url if url isnt "/login"

        @scope.loginParams = =>
            nextState: @state.current.default or @state.current.name
            nextParams: angular.toJson(@state.params)

        @scope.shouldShowAddEntity = =>
            return false unless @isInTopic()
            return @scope.user.hasAddPermission(@TopicsFactory.topic.ontology_as_mod)

        @scope.shouldShowTopicSearch = =>
            in_topic = @isInTopic()
            in_wrong_state = @isInEmptyState() or @isInInvite() or @isInHome()
            in_topic and not in_wrong_state

        @scope.toggleUserMenu = @toggleUserMenu
        @scope.closeUserMenu  = @closeUserMenu

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

    toggleUserMenu: =>
        @scope.userMenuOpened = not @scope.userMenuOpened

    closeUserMenu: (evt)=>
        clickedOnToggle = (e)=>
            boundClick = $(e.target).attr('ng-click') or
                         $(e.target).parent().attr('ng-click')
            boundClick is 'toggleUserMenu()'

        if not clickedOnToggle(evt)
            @scope.userMenuOpened = false



angular.module('detective.controller').controller 'headerCtrl', HeaderCtrl