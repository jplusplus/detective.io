angular.module('detective').directive "watchLoginMandatory", ["$rootScope", "$location", "User", ($root, $location, User) ->
    link: () ->
        $root.$on "$routeChangeStart", (event, current) -> 
            if current.auth and not User.is_logged                
                next = $location.url()
                $location.url("/login?next=#{next}") 
]