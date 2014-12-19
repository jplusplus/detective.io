class window.HeaderCtrl
    @$inject: ['$scope', '$state', 'Common', 'User', 'TopicsFactory', '$location']

    constructor: (@scope, @state, @Common, @User, @TopicsFactory, @location)->
        @scope.user = @User
        @scope.userMenuOpened = false
        # Watch current topic
        @scope.$watch (=>@TopicsFactory.topic), (topic)=> @scope.topic = topic

        @scope.shouldShowTopicSearch = @isInTopic
        @scope.shouldShowAddEntity = =>
            @isInTopic() and @scope.user.hasAddPermission(@TopicsFactory.topic.ontology_as_mod)


        @scope.toggleUserMenu = @toggleUserMenu
        @scope.closeUserMenu  = @closeUserMenu
        @scope.goToMyProfile  = @goToMyProfile
        @scope.goToMySettings = @goToMySettings

    isInTopic: => @state.params.topic?

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




angular.module('detective').controller 'headerCtrl', HeaderCtrl