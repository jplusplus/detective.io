angular.module('detective.config').run [
    '$rootScope'
    '$location'
    ($rootScope, $location)->
        # wait for the DOM to be loaded
        $rootScope.$on '$viewContentLoaded', ->
            # if location search params contain a scollTo
            hash = $location.search().scrollTo
            if hash?
                elem = $("##{hash}")
                if elem and elem.offset()?

                    $('html, body').animate(
                        scrollTop: elem.offset().top,
                        200
                    )
]