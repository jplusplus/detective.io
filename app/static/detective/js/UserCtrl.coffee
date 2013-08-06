# See also :
# http://blog.brunoscopelliti.com/deal-with-users-authentication-in-an-angularjs-web-app
UserCtrl = ($scope, $http, $location, $routeParams, User) ->

    $scope.user = User
    $scope.next = $routeParams.next or "/"

    $scope.login = ->
        config = 
            method: "POST"
            url: "/api/v1/user/login/"
            data: 
                username    : $scope.username
                password    : $scope.password
                remember_me : $scope.remember_me or false
            headers:
                "Content-Type": "application/json"
      
        # succefull login
        $http(config).then( (responce) ->   
            if responce.data? and responce.data.success
                User.set
                    is_logged: true
                    username : $scope.username
                # Redirect to the next URL
                $location.url($scope.next)
            else
                User.set
                    is_logged: false
                    username : ''
        # failled login
        , ->
            User.set
                is_logged: false
                username : ''
        )

    $scope.logout = ->
        config = 
            method: "GET"
            url: "/api/v1/user/logout/"
            headers:
                "Content-Type": "application/json"

        # succefull logout
        $http(config).then (responce) ->            
            if responce.data? and responce.data.success
                User.set
                    is_logged: false
                    username : ''



UserCtrl.$inject = ["$scope", "$http", "$location", "$routeParams", "User"]