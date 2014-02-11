# See also :
# http://blog.brunoscopelliti.com/deal-with-users-authentication-in-an-angularjs-web-app
class UserCtrl
    # Injects dependancies
    @$inject : ["$scope", "$http", "$location", "$routeParams", "User", "Page", "$rootElement"]
    # Public method to resolve
    @resolve:
        user: ($rootScope, $route, $q, $location, Common)->
            notFound    = ->
                deferred.reject()
                $location.path "/404"
                deferred
            deferred    = $q.defer()
            routeParams = $route.current.params
            # Checks that the current topic and user exists together
            if routeParams.username?
                # Retreive the topic for this user
                params =
                    type    : "user"
                    username: routeParams.username
                Common.get params, (data)=>
                    # Stop if it's an unkown topic
                    return notFound() unless data.objects and data.objects.length
                    # Resolve the deffered result
                    deferred.resolve(data.objects[0])
            # Reject now
            else return notFound()
            # Return a deffered object
            deferred.promise

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
        @scope.resetPassword = @resetPassword
        @scope.resetPasswordConfirm = @resetPasswordConfirm
        # Set page title with no title-case
        switch @location.path()
            when "/signup"
                @Page.title "Sign up", false
            when "/login"
                @Page.title "Log in", false
            when "/account/activate"
                @Page.title "Activate your account", false
                @readToken()
            when "/account/reset-password"
                @Page.title "Reset password", false
            when "/account/reset-password-confirm"
                @Page.title "Enter a new password", false

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
            data = response.data
            # Interpret the respose
            if data? and data.success
                @User.set
                    is_logged   : true
                    is_staff    : data.is_staff
                    username    : data.username
                    permissions : data.permissions
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
        @http(config)
            .success (response) =>
                # Turn off loading mode
                @scope.loading = false
                @scope.signupSucceed = true
                    # Delete error
                delete @scope.error
            .error (message)=>
                # Turn off loading mode
                @scope.loading = false
                @scope.signupSucceed = false
                # Record the error
                @scope.error = message if message?

    resetPassword: =>
        config =
            method: "POST"
            url: "/api/common/v1/user/reset_password/"
            data:
                email: @scope.email
            headers:
                "Content-Type": "application/json"
        # Turn on loading mode
        @scope.loading = true
        @http(config)
            .success (response)=>
                # Turn off loading mode
                @scope.loading = false
                @scope.resetEmailSent = true
                delete @scope.error
            .error (message)=>
                @scope.resetEmailSent = false
                @scope.loading = false
                if message?
                    @scope.error = message
                else
                    @unknownError()


    resetPasswordConfirm: =>
        token = @location.search()['token']
        if !token?
            @scope.invalidURL = true
            @scope.error = "Invalid URL, please use the link contained in your password reset email."
        else
            @scope.invalidURL = false
            delete @scope.error
            config =
                method: "POST"
                url: "/api/common/v1/user/reset_password_confirm/"
                data:
                    password: @scope.newPassword
                    token: token
                headers:
                    "Content-Type": "application/json"

            # Turn on loading mode
            @scope.loading = true
            @http(config)
                .success (response)=>
                    # Turn off loading mode
                    @scope.loading = false
                    delete @scope.error
                    @scope.resetPasswordSucceed = true
                .error (response, error)=>
                    @scope.resetPasswordSucceed = false
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
        @http(config)
            .success (response) =>
                @Page.loading false
                @scope.state = true
            .error (message)=>
                @Page.loading false
                @scope.state = false

    unknownError: ()=>
        @scope.error = "An unexpected error happened, sorry for that."

angular.module('detective.controller').controller 'userCtrl', UserCtrl