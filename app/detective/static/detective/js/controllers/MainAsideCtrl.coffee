class MainAsideCtrl
    @$inject: ['$scope', 'Common', 'TopicsFactory', '$location']

    constructor: (@scope, @Common, @TopicsFactory, @location)->
    	@scope.topicsFactory = @TopicsFactory


angular.module('detective.controller').controller 'mainAsideCtrl', MainAsideCtrl