(angular.module 'detective.service').factory 'Group', ['$resource', 'User', ($resource, User) ->
    $resource '/api/detective/common/v1/user/:user_id/groups/?', { user_id : User.id }, {
        collaborator:
            params : { name__contains : '_contributor' }
            method : 'GET'
            isArray : no
        administrator:
            params : { name__contains : '_administrator' }
            method : 'GET'
            isArray : no
    }
]
