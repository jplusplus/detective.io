angular.module('detective.config').run [
        "$rootScope"
        "$state"
        "User"
        "TopicsFactory"
        ($root, $state, User, TopicsFactory) ->
            $root.$on "$stateChangeStart", (e, current, params)=>
                admin = current.admin
                return unless admin?
                if params.topic? and params.username?
                    (TopicsFactory.getTopic params.topic, params.username).then (data) =>
                        topic = data.ontology_as_mod
                        if not (User.hasAdministratePermission topic)
                            do e.preventDefault
                            $state.go "403"
    ]