angular.module('detective').run [
        "$rootScope"
        "$state"
        "User"
        ($root, $state, User) ->
            $root.$on "$stateChangeStart", (e, current, params)=>
                auth = current.auth
                return unless auth?
                if auth and not User.is_logged
                    e.preventDefault()
                    login_params =
                        nextState:  current.default or current.name
                        nextParams: angular.toJson params
                    $state.go("login", login_params)

                else if not auth and User.is_logged
                    e.preventDefault()
                    $state.go("home.dashboard")


    ]