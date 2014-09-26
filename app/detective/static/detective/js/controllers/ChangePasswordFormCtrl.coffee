class window.ChangePasswordFormCtrl
    @$inject: ['$scope', '$state', '$http', '$timeout',  'User', 'Page']
    constructor: (@scope, @state, @http, @timeout, @User, @Page)->
        console.log 'ChangePasswordFormCtrl'
        @showPasswordChanged = no
        @new_password = undefined

    changePassword: (form)=>
        @submitted = true
        return unless form.$valid
        @loading = true
        @http.post('/api/detective/common/v1/user/change_password/', new_password: @new_password)
            .success(@onPasswordChanged)
            .error(@onError)

    onPasswordChanged: (response)=>
        @loading = false
        @showPasswordChanged = true
        delete @error
        @timeout( =>
            @showPasswordChanged = false
        , 2000)

    onError: (message)=>
        @loading = false
        @showPasswordChanged = false
        @error = message



angular.module('detective.controller').controller 'changePasswordFormCtrl', ChangePasswordFormCtrl