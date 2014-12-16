class window.AccountSettingsCtrl
    @$inject: ['Page']

    constructor: (Page)->
        Page.title 'Settings'

angular.module('detective').controller 'accountSettingsCtrl', AccountSettingsCtrl