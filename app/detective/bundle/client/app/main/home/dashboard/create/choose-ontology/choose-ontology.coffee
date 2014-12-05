angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('user-topic-create.choose-ontology',
        templateUrl: '/partial/main/home/dashboard/create/choose-ontology/choose-ontology.html'
    )
]