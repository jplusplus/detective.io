angular.module('detective.config').run [
    '$rootScope'
    '$location'
    ($rootScope, $location)->
        scrollTo = ->
            # if location search params contain a scollTo
            hash = $location.search().scrollTo
            if hash?
                elem = $("##{hash}")
                if elem and elem.offset()?

                    $('html, body').animate(
                        scrollTop: elem.offset().top - 50,
                        200
                    )
        # wait for the DOM to be loaded
        $rootScope.$on '$viewContentLoaded', scrollTo

        $rootScope.$on 'scrollTo:trigger', scrollTo
]