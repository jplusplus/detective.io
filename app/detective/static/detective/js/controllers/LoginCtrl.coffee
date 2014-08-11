class LoginCtrl
    # Injects dependencies
    @$inject : ["$scope", "$stateParams", "$state", "Auth", "User", "Page", "$rootElement"]

    constructor: (@scope, @stateParams, @state, @Auth, @User, @Page, @rootElement)->
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        @scope.user       = @User
        @scope.nextState  = @stateParams.nextState
        @scope.nextParams = angular.fromJson(@stateParams.nextParams or {})
        @scope.loading    = false
        # ──────────────────────────────────────────────────────────────────────
        # Scope method
        # ──────────────────────────────────────────────────────────────────────
        @scope.login   = @login
        @scope.logout  = @logout
        # Page settings
        @Page.loading no
        @Page.title "Log in", false

    # ──────────────────────────────────────────────────────────────────────────
    # Class methods
    # ──────────────────────────────────────────────────────────────────────────
    # Record the error
    loginError: (error)=> @scope.error = error if error?

    login: =>
        # Trigger the event waited in the autofill directive
        @scope.$broadcast 'autofill:update'
        # Catch a bug with angular and browser autofill
        # Open issue https://github.com/angular/angular.js/issues/1460
        unless @scope.username? or @scope.password?
            @scope.username = @rootElement.find("[ng-model=username]").val()
            @scope.password = @rootElement.find("[ng-model=password]").val()
        # Credidentials
        credidentials =
            username   : @scope.username
            password   : @scope.password
            remember_me: @scope.remember_me or false
        # Turn on loading mode
        @scope.loading = true
        # succefull login
        @Auth.login(credidentials).then( (response) =>
            # Turn off loading mode
            @scope.loading = false
            data = response.data
            # Interpret the respose
            if data? and data.success
                # Redirect to the next URL
                @state.go "home.dashboard"
                # Delete error
                delete @scope.error
            else
                # Error status
                @loginError(response.data.error_message)
        # Error status
        , (response)=> @loginError(response.data.error_message) )


angular.module('detective.controller').controller 'loginCtrl', LoginCtrl