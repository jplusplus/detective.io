angular.module("detective.service").factory "Auth", [
  "$http",
  "$q",
  "$rootScope",
  "User",
  ($http, $q, $rootScope, User)->
    new class Auth
      constructor: ->
        # Watch current token
        $rootScope.$on "user:login", @load
        # User already logged in
        $rootScope.$broadcast "user:login" if @isAuthenticated()

      load: ->
        deferred = $q.defer()
        # User just log in
        if User.is_logged
          # Load its user permission
          $http.get("/api/detective/common/v1/user/me/").then (response)=>
            if response.data?
              # Save profile
              User.set response.data
              # User is now fully loaded
              $rootScope.$broadcast "user:loaded", User
              deferred.resolve User
              User
            else
              deferred.reject("User not authenticated.")
        else
          deferred.reject("User not authenticated.")

      login: (credentials)->
        # succefull login
        return $http.post("/api/detective/common/v1/user/login/", credentials).then( (response)=>
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

      isAuthenticated: -> User.username isnt null and User.username isnt ""
]
