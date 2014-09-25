angular.module("detective.directive").directive 'checkPassword', [
    'Auth', 'User'
    (Auth, User)->
        restrict: 'A'
        require: [ '?^form', 'ngModel' ]
        link: (scope, elem, attr, ctrls)->
            formCtrl  = ctrls[0]
            modelCtrl = ctrls[1]
            checkPassword = ->
                formCtrl.$pending = true
                params =
                    username: User.username
                    password: modelCtrl.$viewValue

                # get model value
                Auth.login(params).then (response)->
                    formCtrl.$pending = false
                    modelCtrl.$setValidity 'incorrect_password', response.data.success

            elem.on "blur", checkPassword
]