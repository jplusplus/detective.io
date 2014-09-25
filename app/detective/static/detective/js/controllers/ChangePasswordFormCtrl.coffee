class window.ChangePasswordFormCtrl
    @$inject: ['$scope', '$state', '$http', 'User', 'Page']
    constructor: (@scope, @state, @http, @User, @Page)->
        @Page.title ''
        # Scope variables
        @scope.password_changed = no

        # Scope methods
        @scope.changePassword = @changePassword

    changePassword: (form)=>
        @scope.submitted = true
        return unless form.$valid
        @scope.loading   = true
        @http.post('/api/detective/common/v1/user/change_password/', new_password: @scope.new_password)
            .success (response)=>
                @scope.loading = false
                @scope.password_changed = true
                delete @scope.error
            .error (message)=>
                @scope.loading = false
                @scope.password_changed = false
                @scope.error = message





angular.module('detective.controller').controller 'changePasswordFormCtrl', ChangePasswordFormCtrl