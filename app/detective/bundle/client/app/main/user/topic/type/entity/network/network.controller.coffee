class window.IndividualNetworkCtrl
    # Injects dependencies
    @$inject: ['$scope', '$stateParams', 'graphnodes']
    constructor: (@scope, @stateParams, @graphnodes)->
        @scope.graphnodes = @graphnodes or []

angular.module('detective').controller 'individualNetworkCtrl', IndividualNetworkCtrl
# EOF
