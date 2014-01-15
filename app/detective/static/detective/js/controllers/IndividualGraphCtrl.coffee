class IndividualGraphCtrl
    # Injects dependancies
    @$inject: ['$scope', '$routeParams', 'Individual', '$http', 'Page', '$filter']

    updateNodes : =>
        @scope.rangedisabled = yes
        (@http.get "/api/#{@scope.topic}/v1/#{@scope.type}/#{@scope.id}/graph?depth=#{@scope.depth}").success (data) =>
            @scope.graphnodes = data
            @Page.loading false
            @scope.rangedisabled = no

    constructor: (@scope, @routeParams, @Individual, @http, @Page, @filter) ->
        @Page.loading true

        @scope.graphnodes = []

        @scope.depth = 1
        @scope.rangedisabled = yes

        @scope.topic = @routeParams.topic
        @scope.type  = @routeParams.type
        @scope.id    = @routeParams.id
        params =
            topic: @scope.topic
            type : @scope.type
            id   : @scope.id

        @Individual.get params, (data) =>
            @Page.title (@filter "individualPreview") data

        @scope.$watch 'depth', =>
            do @updateNodes

angular.module('detective').controller 'individualGraphCtrl', IndividualGraphCtrl
