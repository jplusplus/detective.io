class HeaderCtrl
    @$inject: ['$scope', 'Common', '$location']

    constructor: (@scope, @Common, @location)->
        @scope.$watch (=>@location.url()), (url)=>
            @scope.nextLogin = url if url isnt "/login"
        

angular.module('detective.controller').controller 'headerCtrl', HeaderCtrl