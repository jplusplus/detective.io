class window.DeleteAccountCtrl
    @$inject: [ '$rootScope', '$scope', '$state', '$timeout', '$modal', '$http', 'User', 'Page', 'constants.events' ]

    REDIRECT_SUCCESS_TIMEOUT: 1800

    constructor: (@rootScope, @scope, @state, @timeout, @modal, @http, @User, Page, @EVENTS)->
        Page.title 'Remove your account'
        # Scope variables
        @scope.submitted = false
        @scope.check_password = undefined
        # Scope nethods
        @scope.deleteAccount = @submit
        @scope.goToDasbhoard = @goToDasbhoard

        @scope.shouldShowIncorrectPassword = (form_field)=>
            required_error  = form_field.$error.required
            incorrect_error = form_field.$error.incorrect_password
            @scope.submitted and not required_error and incorrect_error

        @scope.shouldShowRequiredPassword = (form_field)=>
            @scope.submitted and form_field.$error.required

    openConfirmModal: (form)=>
        @pending_listener() if @pending_listener?
        @scope.submitted = true
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

    goToDasbhoard: =>
        @state.go 'home.dashboard'

angular.module('detective.controller').controller 'deleteAccountCtrl', DeleteAccountCtrl