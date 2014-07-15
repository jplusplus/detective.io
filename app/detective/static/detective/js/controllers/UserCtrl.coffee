# See also :
# http://blog.brunoscopelliti.com/deal-with-users-authentication-in-an-angularjs-web-app
class UserCtrl
    # Injects dependancies
    @$inject : ["$scope", "$http", "$location", "$stateParams", "$state", "Auth", "User", "Page", "$rootElement"]
    # Public method to resolve
    @resolve:
        user: [
            "$rootScope",
            "$stateParams",
            "$state",
            "$q",
            "Common",
            ($rootScope, $stateParams, $state, $q, Common)->
                notFound    = ->
                    deferred.reject()
                    $state.go "404"
                    deferred
                deferred    = $q.defer()
                # Checks that the current topic and user exists together
                if $stateParams.username?
                    # Retreive the topic for this user
                    params =
                        type    : "user"
                        username: $stateParams.username
                    Common.get params, (data)=>
                        # Stop if it's an unkown topic
                        return notFound() unless data.objects and data.objects.length
                        # Resolve the deffered result
                        deferred.resolve data.objects[0]
                # Reject now
                else return notFound()
                # Return a deffered object
                deferred.promise
        ]

    constructor: (@scope, @http, @location, @stateParams, @state, @Auth, @User, @Page, @rootElement)->
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        @scope.user    = @User
        @scope.next    = @stateParams.next or "/"
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
        if @state.is("signup")
            @Page.title "Request an account", false
        else if @state.is("login")
            @Page.title "Log in", false
        else if @state.is("activate")
            @Page.title "Activate your account", false
            @readToken()
        else if @state.is("reset-password")
            @Page.title "Reset password", false
        else if @state.is("reset-password-confirm")
            @Page.title "Enter a new password", false

        @Page.loading no

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
                @location.url(@scope.next)
                # Delete error
                delete @scope.error
            else
                # Error status
                @loginError(response.data.error_message)
        # Error status
        , (response)=> @loginError(response.data.error_message) )

    signup: =>
        data =
            username: @scope.username
            email   : @scope.email
            password: @scope.password
        # Turn on loading mode
        @scope.loading = true
        # succefull login
        @http.post("/api/common/v1/user/signup/", data)
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
        # Turn on loading mode
        @scope.loading = true
        @http.post("/api/common/v1/user/reset_password/", email: @scope.email)
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
        token = @stateParams.token
        if !token?
            @scope.invalidURL = true
            @scope.error = "Invalid URL, please use the link contained in your password reset email."
        else
            @scope.invalidURL = false
            delete @scope.error
            data =
                password: @scope.newPassword
                token: token
            # Turn on loading mode
            @scope.loading = true
            @http.post("/api/common/v1/user/reset_password_confirm/", data)
                .success (response)=>
                    # Turn off loading mode
                    @scope.loading = false
                    delete @scope.error
                    @scope.resetPasswordSucceed = true
                .error (response, error)=>
                    @scope.resetPasswordSucceed = false
                    @scope.error = response.data.error_message if response.data.error_message?


    logout: =>
        next_url = @location.url()
        @Auth.logout().then =>
            # Redirect to login form
            @location.url("/login?next=#{next_url}")

    readToken: =>
        @Page.loading(true)
        # Submits the token for activation
        @http.get("/api/common/v1/user/activate/?token=#{@stateParams.token}")
            .success (response) =>
                @Page.loading false
                @scope.state = true
            .error (message)=>
                @Page.loading false
                @scope.state = false

    unknownError: ()=>
        @scope.error = "An unexpected error happened, sorry for that."

angular.module('detective.controller').controller 'userCtrl', UserCtrl