angular.module('detective').config ["$provide", ($provide)->
    return $provide.decorator "$rootScope", [
        "$delegate"
        ($delegate) ->
            $delegate.safeApply = (fn) ->
                phase = $delegate.$$phase
                if phase is "$apply" or phase is "$digest"
                    fn()  if fn and typeof fn is "function"
                else
                    $delegate.$apply fn
                return

            $delegate
    ]
]