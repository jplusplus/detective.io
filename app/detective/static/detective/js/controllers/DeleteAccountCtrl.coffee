class window.DeleteAccountCtrl
    @$inject: [ '$rootScope', '$scope', '$state', '$timeout', '$modal', '$http', 'Auth', 'User', 'Page', 'constants.events' ]

    REDIRECT_SUCCESS_TIMEOUT: 1000

    constructor: (@rootScope, @scope, @state, @timeout, @modal, @http, @Auth, @User, Page, @EVENTS)->
        Page.title 'Remove your account'
        # Scope variables
        @scope.submitted = false
        @scope.check_password = undefined
        # Scope nethods
        @scope.checkPassword = @checkPassword
        @scope.cuddleCuddle  = @cuddleCuddle


    openConfirmModal: =>
        modalInstance = @modal.open
            templateUrl: '/partial/account.delete.confirm-modal.html'
            controller: 'confirmAccountDeleteModalCtrl as modal'

        modalInstance.result.then (confirmed)=>
            @deleteAccount() if confirmed is true

    checkPassword: (form)=>
        return unless form.$valid
        @scope.submitted = true
        params =
            username: @User.username
            password: @scope.check_password

        @Auth.login(params).then (response)=>
            data = response.data
            if data.success
                @openConfirmModal()
            else
                incorrect_password = data.error_code is 'incorrect_password_or_email'
                @scope.error =
                    incorrect_password: incorrect_password

    deleteAccount: =>
        @http.delete("/api/detective/common/v1/user/#{@User.id}/").then (response)=>
            if response.status in [200, 204]
                @scope.deleted = true
                @User.set
                    is_logged  : false
                    is_staff   : false
                    username   : null
                    permissions: []
                @rootScope.$broadcast @EVENTS.user.logout, @User
                @timeout(=>
                    @state.go 'home'
                , @REDIRECT_SUCCESS_TIMEOUT)

    cuddleCuddle: =>
        @state.go 'home.dashboard'

angular.module('detective.controller').controller 'deleteAccountCtrl', DeleteAccountCtrl