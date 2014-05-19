class HeaderCtrl
    @$inject: ['$scope', 'Common']

    constructor: (@scope, @Common)->
        super

angular.module('detective.controller').controller 'headerCtrl', HeaderCtrl