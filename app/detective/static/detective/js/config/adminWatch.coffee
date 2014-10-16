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
                    topic = TopicsFactory.getTopic params.topic, params.username
                    if not (User.hasAdministratePermission topic.ontology_as_mod)
                        do e.preventDefault
                        $state.go "403"
    ]