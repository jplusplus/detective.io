angular.module('detective.config').run [
        "$rootScope"
        "$state"
        "User"
        ($root, $state, User) ->
            $root.$on "$stateChangeStart", (e, current, params)=>
                if current.auth and not User.is_logged
                    e.preventDefault()
                    login_params = 
                        nextState:  current.name
                        nextParams: angular.toJson params
                    $state.go("login", login_params)
    ]