angular.module('detective.config').run [
        "$rootScope"
        "$state"
        "User"
        (@root, @state, User) ->
            @root.$on "$stateChangeStart", (e, current)=>
                # e.preventDefault()
                nextState  = current.name
                nextParams = angular.toJson @state.params
                if current.auth and not User.is_logged
                    stateParams = 
                        nextState: nextState
                        nextParams: nextParams
                    @state.go "login", stateParams
    ]