angular.module("detective.directive").directive 'checkPassword', [
    'Auth', 'User'
    (Auth, User)->
        restrict: 'A'
        require: 'ngModel'
        link: (scope, elem, attr, ctrl)->
            checkPassword = ->
                params =
                    username: User.username
                    password: ctrl.$viewValue

                # get model value
                Auth.login(params).then (response)->
                    ctrl.$setValidity 'incorrect_password', response.data.success

            elem.on "blur", checkPassword
]