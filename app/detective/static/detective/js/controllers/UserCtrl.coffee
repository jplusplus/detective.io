# See also :
# http://blog.brunoscopelliti.com/deal-with-users-authentication-in-an-angularjs-web-app
class window.UserCtrl
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

    # Injects dependencies
    @$inject : ["$scope", "$http", "$location", "$stateParams", "$state", "Auth", "User", "Page", "$rootElement"]

    constructor: (@scope, @http, @location, @stateParams, @state, @Auth, @User, @Page, @rootElement)->
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        @scope.user    = @User
        @scope.nextState  = @stateParams.nextState
        @scope.nextParams = angular.fromJson(@stateParams.nextParams or {})
        # ──────────────────────────────────────────────────────────────────────
        # Scope method
        # ──────────────────────────────────────────────────────────────────────
        @scope.loading = false
        @scope.logout  = @logout
        @scope.signup  = @signup

        @scope_vars = ['username', 'password', 'password2', 'email', 'terms']

        # add watch for scope values and set them as not submitted if value
        # changes
        angular.forEach @scope_vars, (name)=>
            @scope.$watch name, =>
                @scope["#{name}Submitted"] = false
                @scope.submitted = false

        @scope.$watch 'submitted', (v)=>
            return unless v
            angular.forEach @scope_vars, (name)=>
                @scope["#{name}Submitted"] = true



        @scope.resetPassword = @resetPassword
        @scope.resetPasswordConfirm = @resetPasswordConfirm
        # Set page title with no title-case
        if @state.is("signup") or @state.is("signup-invitation")
            @Page.title "Request an account", false
        else if @state.is("activate")
            @Page.title "Activate your account", false
            @readToken()
        else if @state.is("reset-password")
            @Page.title "Reset password", false
        else if @state.is("reset-password-confirm")
            @Page.title "Enter a new password", false
        else if (@state.is "subscribe")
            @Page.title "Subscribe to a paid plan", false
            # We need @scope.subscription if we're on the subscription page
            @scope.subscription =
                plan : @stateParams.plan or 'hank'
                username : User.username

        @Page.loading no


    # ──────────────────────────────────────────────────────────────────────────
    # Class methods
    # ──────────────────────────────────────────────────────────────────────────

    signup: (form) =>
        @scope.submitted = yes
        return if form.$invalid
        data =
            username: @scope.username
            email   : @scope.email
            password: @scope.password
        # Add token during invitation
        if @state.is("signup-invitation")
            data["token"] = @stateParams.token
        # Turn on loading mode
        @scope.loading = true
        # succefull login
        @http.post("/api/detective/common/v1/user/signup/", data)
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

    subscribe: (form) =>

    resetPassword: =>
        # Turn on loading mode
        @scope.loading = true
        @http.post("/api/detective/common/v1/user/reset_password/", email: @scope.email)
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
            @http.post("/api/detective/common/v1/user/reset_password_confirm/", data)
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
            login_params =
                nextState: @state.current.default or @state.current.name
                nextParams: angular.toJson @state.params

            @state.go 'login', login_params

    readToken: =>
        @Page.loading(true)
        # Submits the token for activation
        @http.get("/api/detective/common/v1/user/activate/?token=#{@stateParams.token}")
            .success (response) =>
                @Page.loading false
                @scope.state = true
            .error (message)=>
                @Page.loading false
                @scope.state = false

    unknownError: ()=>
        @scope.error = "An unexpected error happened, sorry for that."

angular.module('detective.controller').controller 'userCtrl', UserCtrl