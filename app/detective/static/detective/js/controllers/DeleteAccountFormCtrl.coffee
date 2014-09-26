class window.DeleteAccountFormCtrl
    @$inject: [ '$rootScope', '$scope', '$state', '$timeout', '$modal', '$http', 'User', 'constants.events' ]

    REDIRECT_SUCCESS_TIMEOUT: 1800

    constructor: (@rootScope, @scope, @state, @timeout, @modal, @http, @User, @EVENTS)->
        console.log 'DeleteAccountFormCtrl'
        # Scope variables
        @submitted = false
        @check_password = undefined

    shouldShowIncorrectPassword: (form_field)=>
        required_error  = form_field.$error.required
        incorrect_error = form_field.$error.incorrect_password
        @submitted and not required_error and incorrect_error

    shouldShowRequiredPassword:(form_field)=>
        @submitted and form_field.$error.required

    openConfirmModal: (form)=>
        @pending_listener() if @pending_listener?
        @submitted = true
        return unless form.$valid
        @modalInstance = @modal.open
            templateUrl: '/partial/account.delete.confirm-modal.html'
            controller: 'confirmAccountDeleteModalCtrl as modal'

        @modalInstance.result.then (confirmed)=>
            @deleteAccount() if confirmed is true
            @modalInstance = undefined

    submit: (form)=>
        # if form is currently validing we wait for its $pending
        # value to be false
        if form.$pending['check_password']
            @pending_listener = @scope.$watch(->
                form.$pending['check_password']
            , (is_pending)=>
                if is_pending is false
                    @openConfirmModal(form)
            , true)
        else
            @openConfirmModal(form)

    deleteAccount: =>
        @loading = true
        @http.delete("/api/detective/common/v1/user/#{@User.id}/").then (response)=>
            if response.status in [200, 204]
                @loading = false
                @deleted = true
                @User.set
                    is_logged  : false
                    is_staff   : false
                    username   : null
                    permissions: []
                @rootScope.$broadcast @EVENTS.user.logout, @User
                @timeout(=>
                    @state.go 'home'
                , @REDIRECT_SUCCESS_TIMEOUT)

    goToDasbhoard: =>
        @state.go 'home.dashboard'

angular.module('detective.controller').controller 'deleteAccountFormCtrl', DeleteAccountFormCtrl