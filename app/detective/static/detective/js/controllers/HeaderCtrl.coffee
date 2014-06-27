class HeaderCtrl
    @$inject: ['$scope', 'Common', 'TopicsFactory', '$location']

    constructor: (@scope, @Common, @TopicsFactory, @location)->
        # Watch URL change to determine the login destination
        @scope.$watch (=>@location.url()), (url)=>
            @scope.nextLogin = url if url isnt "/login"


angular.module('detective.controller').controller 'headerCtrl', HeaderCtrl