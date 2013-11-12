# See also :
# http://blog.brunoscopelliti.com/deal-with-users-authentication-in-an-angularjs-web-app
class UserCtrl

    # Injects dependancies
    @$inject : ["$scope", "$http", "$location", "$routeParams", "User", "Page", "$rootElement"]

    constructor: (@scope, @http, @location, @routeParams, @User, @Page, @rootElement)->
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        @scope.user    = @User
        @scope.next    = @routeParams.next or "/"
        # ──────────────────────────────────────────────────────────────────────
        # Scope method
        # ──────────────────────────────────────────────────────────────────────
        @scope.loading = false
        @scope.login   = @login
        @scope.logout  = @logout
        @scope.signup  = @signup
        # Set page title with no title-case
        switch @location.path()
            when "/signup"
                @Page.title "Sign up", false
            when "/login"
                @Page.title "Log in", false
            when "/account/activate"
                @Page.title "Activate your account", false
                @readToken()



    # ──────────────────────────────────────────────────────────────────────────
    # Class methods
    # ──────────────────────────────────────────────────────────────────────────
    loginError: (error)=>
        @User.set
            is_logged: false
            is_staff : false
            username : ''
        # Record the error
        @scope.error = error if error?

    login: (el)=>
        # Catch a bug with angular and browser autofill
        # Open issue https://github.com/angular/angular.js/issues/1460
        unless @scope.username? or @scope.password?
            @scope.username = @rootElement.find("[ng-model=username]").val()
            @scope.password = @rootElement.find("[ng-model=password]").val()

        config =
            method: "POST"
            url: "/api/common/v1/user/login/"
            data:
                username    : @scope.username
                password    : @scope.password
                remember_me : @scope.remember_me or false
            headers:
                "Content-Type": "application/json"
        # Turn on loading mode
        @scope.loading = true
        # succefull login
        @http(config).then( (response) =>
            # Turn off loading mode
            @scope.loading = false
            # Interpret the respose
            if response.data? and response.data.success
                @User.set
                    is_logged: true
                    is_staff : response.data.is_staff
                    username : response.data.username
                # Redirect to the next URL
                @location.url(@scope.next)
                # Delete error
                delete @scope.error
            else
                # Error status
                @loginError(response.data.error_message)
        # Error status
        , (response)=> @loginError(response.data.error_message) )

    signup: =>
        config =
            method: "POST"
            url: "/api/common/v1/user/signup/"
            data:
                username: @scope.username
                email   : @scope.email
                password: @scope.password
            headers:
                "Content-Type": "application/json"
        # Turn on loading mode
        @scope.loading = true
        # succefull login
        @http(config).then (response) =>
            # Turn off loading mode
            @scope.loading = false
            # Interpret the respose
            if response.data?
                @scope.signupSucceed = true
                # Delete error
                delete @scope.error
            else
                # Record the error
                @scope.error = response.data.error_message if response.data.error_message?

    logout: =>
        config =
            method: "GET"
            url: "/api/common/v1/user/logout/"
            headers:
                "Content-Type": "application/json"
        # Turn on loading mode
        @scope.loading = true
        # succefull logout
        @http(config).then (response) =>
            # Turn off loading mode
            @scope.loading = false
            # Interpret the respose
            if response.data? and response.data.success
                # Redirect to login form
                @location.path("/login")
                # Update user data
                @User.set
                    is_logged: false
                    is_staff : false
                    username : ''
    readToken: =>
        @Page.loading(true)
        config =
            method: "GET"
            url: "/api/common/v1/user/activate/"
            params:
                token: @routeParams.token
        # Submits the token for activation
        @http(config).then (response) =>
            @Page.loading false
            @scope.state = response.data? and response.data.success

angular.module('detective').controller 'userCtrl', UserCtrl