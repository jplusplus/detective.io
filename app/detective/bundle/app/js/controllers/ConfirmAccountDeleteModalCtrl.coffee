class window.ConfirmAccountDeleteModalCtrl
    @$inject: ['$modalInstance']

    constructor: (@modalInstance)->
        # pass

    confirm: =>
        @close(true)

    close:(confirm=false)=>
        @modalInstance.close(confirm)


angular.module('detective.controller').controller 'confirmAccountDeleteModalCtrl', ConfirmAccountDeleteModalCtrl