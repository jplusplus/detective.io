angular.module("detective.service").factory "Auth", [
  "$http",
  "$q",
  "$rootScope",
  "User",
  ($http, $q, $rootScope, User)->
    new class Auth
      constructor: ->
        # Watch current token
        $rootScope.$on "user:login", @loadPermissions
        # User already logged in
        $rootScope.$broadcast "user:login" if @isAuthenticated()

      loadPermissions: ->
        # User just log in
        if User.is_logged
          # Load its user profile
          $http.get("/api/common/v1/user/permissions/").then (response)=>
            if response.data?
              # Save profile
              User.set permissions: response.data.permissions
              # User is now fully loaded
              $rootScope.$broadcast "user:loaded", User

      login: (credentials)->
        # succefull login
        return $http.post("/api/common/v1/user/login/", credentials).then( (response)=>
          data = response.data
          # Interpret the respose
          if data? and data.success
            User.set
              is_logged   : true
              is_staff    : !! data.is_staff
              username    : data.username
              permissions : []
            # Propagate login
            $rootScope.$broadcast "user:login", User
          return response
        )

      logout: ->
        # succefull logout
        return $http.get("/api/common/v1/user/logout/").then( (response)=>
          # Interpret the respose
          if response.data? and response.data.success
            # Update user data
            User.set
              is_logged  : false
              is_staff   : false
              username   : null
              permissions: []
            # Propagate logout
            $rootScope.$broadcast "user:logout", User
          return response
        )

      isAuthenticated: -> User.is_logged?
]
