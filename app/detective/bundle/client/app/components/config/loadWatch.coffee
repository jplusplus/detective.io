angular.module('detective').run [
        "$rootScope"
        "$state"
        "Page"
        ($root, $state, Page) ->
            $root.$on "$stateChangeStart", (e, current, params)=>
                Page.loading yes
            $root.$on "$stateChangeSuccess", (e, current, params)=>
                Page.loading no
            $root.$on "$stateChangeError", (e, current, params)=>
                Page.loading no

    ]