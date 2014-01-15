class IndividualGraphCtrl
    # Injects dependancies
    @$inject: ['$scope', '$routeParams', 'Individual', '$http', 'Page', '$filter']

    constructor: (@scope, @routeParams, @Individual, $http, @Page, @filter) ->
        Page.loading true

        @scope.graphnodes = []

        @scope.topic = @routeParams.topic
        @scope.type  = @routeParams.type
        @scope.id    = @routeParams.id
        params =
            topic: @scope.topic
            type : @scope.type
            id   : @scope.id

        @Individual.get params, (data) =>
            @Page.title (@filter "individualPreview") data

            ($http.get "/api/#{@scope.topic}/v1/#{@scope.type}/#{@scope.id}/graph").success (data) =>
                @scope.graphnodes = data
                Page.loading false

angular.module('detective').controller 'individualGraphCtrl', IndividualGraphCtrl
