# See also :
# http://blog.brunoscopelliti.com/deal-with-users-authentication-in-an-angularjs-web-app
UserCtrl = ($scope, $http, User) ->

    $scope.user = User

    $scope.login = ->
        config = 
            method: "POST"
            url: "/api/v1/user/login/"
            data: 
                username: $scope.username
                password: $scope.password
            headers:
                "Content-Type": "application/json"
      
        # succefull login
        $http(config).success( (data, status, headers, config) ->            
            if data? and data.success
                User.is_logged = true
                User.username   = $scope.username
            else
                User.is_logged = false
                User.username   = ""
        # failled login
        ).error (data, status, headers, config) ->
            User.is_logged = false
            User.username   = ""

    $scope.logout = ->
        config = 
            method: "GET"
            url: "/api/v1/user/logout/"
            headers:
                "Content-Type": "application/json"

        # succefull logout
        $http(config).success (data, status, headers, config) ->            
            if data? and data.success
                User.is_logged = false
                User.username   = ""        



UserCtrl.$inject = ["$scope", "$http", "User"]