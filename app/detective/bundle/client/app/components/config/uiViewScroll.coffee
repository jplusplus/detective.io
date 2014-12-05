angular.module('detective').config [
    "$provide"
    ($provide) ->
        $provide.decorator '$uiViewScroll', ($delegate) ->
            (uiViewElement) ->
                window.scrollTo 0, 0
]
