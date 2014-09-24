class window.RemoveUserCtrl
    @$inject: ['$scope', '$modal', 'Auth', 'User', 'Page']
    constructor: (@scope, @modal,@Auth, @User, Page)->
        Page.title 'Remove your account'
        @scope.submitted = false
        @scope.check_password = undefined


    openConfirmModal: =>
        modalInstance = @modal.open
            templateUrl: '/partials/account.delete.confirm-modal.html'
            controller: 'confirmAccountDeleteModalCtrl as modal'

        modalInstance.result.then (confirmed)=>
            @deleteAccount() if confirmed is true

    checkPassword: (form)=>
        return unless form.$valid

        @Auth.login(params).then (response)=>
            if data.success
                @openConfirmModal()
            else
                incorrect_password = data.error_code is 'incorrect_password_or_email'
                @scope.error
                    incorrect_password: incorrect_password


    deleteAccount: =>
        @http.delete('/api/detective/common/v1/user/me/').then (response)=>
            if response.status in [200, 202, 204]
                @scope.deleted = true
                @scope.submitted = false




angular.module('detective.controller').controller 'removeUserCtrl', RemoveUserCtrl