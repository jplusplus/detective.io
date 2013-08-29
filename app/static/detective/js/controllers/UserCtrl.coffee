# See also :
# http://blog.brunoscopelliti.com/deal-with-users-authentication-in-an-angularjs-web-app
class UserCtrl

    # Injects dependancies    
    @$inject : ["$scope", "$http", "$location", "$routeParams", "User"]

    constructor: (@scope, @http, @location, @routeParams, @User)-> 
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

    login: =>
        config = 
            method: "POST"
            url: "/api/v1/user/login/"
            data: 
                username    : @scope.username
                password    : @scope.password
                remember_me : @scope.remember_me or false
            headers:
                "Content-Type": "application/json"       
        # Turn on loading mode
        @scope.loading = true
        # succefull login
        @http(config).then (response) =>   
            # Turn off loading mode
            @scope.loading = false
            # Interpret the respose            
            if response.data? and response.data.success
                @User.set
                    is_logged: true
                    is_staff : response.data.is_staff
                    username : @scope.username
                # Redirect to the next URL
                @location.url(@scope.next)
                # Delete error
                delete @scope.error
            else
                # Error status
                loginError(response.data.reason)            

    logout: =>
        config = 
            method: "GET"
            url: "/api/v1/user/logout/"
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
                @User.set
                    is_logged: false
                    is_staff : false
                    username : ''


angular.module('detective').controller 'userCtrl', UserCtrl