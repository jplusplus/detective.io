class window.HeaderCtrl
    @$inject: ['$scope', '$state', 'Common', 'User', 'TopicsFactory', '$location']

    constructor: (@scope, @state, @Common, @User, @TopicsFactory, @location)->
        @scope.user = @User
        @scope.userMenuOpened = false
        # Watch current topic
        @scope.$watch (=>@TopicsFactory.topic), (topic)=> @scope.topic = topic

        @scope.shouldShowAddEntity = =>
            return false unless @isInTopic()
            return @scope.user.hasAddPermission(@TopicsFactory.topic.ontology_as_mod)

        @scope.shouldShowTopicSearch = =>
            in_topic = @isInTopic()
            in_wrong_state = @isInEmptyState() or @isInInvite() or @isInHome()
            in_topic and not in_wrong_state

        @scope.toggleUserMenu = @toggleUserMenu
        @scope.closeUserMenu  = @closeUserMenu
        @scope.goToMyProfile  = @goToMyProfile
        @scope.goToMySettings = @goToMySettings

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

    goToMyProfile: =>
        @closeUserMenu()
        @state.go "user.me", {username: @User.username}

    goToMySettings: =>
        @closeUserMenu()
        @state.go "user.settings", {username: @User.username}


    closeUserMenu: (evt=false)=>
        clickedOnToggle = (e)=>
            boundClick = $(e.target).attr('ng-click') or
                         $(e.target).parent().attr('ng-click')
            boundClick is 'toggleUserMenu()'

        if evt and not clickedOnToggle(evt)
            @scope.userMenuOpened = false
        else if not evt
            @scope.userMenuOpened = false




angular.module('detective.controller').controller 'headerCtrl', HeaderCtrl