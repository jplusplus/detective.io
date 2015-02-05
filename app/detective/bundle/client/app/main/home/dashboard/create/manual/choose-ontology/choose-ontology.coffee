angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('user-topic-create.manual.choose-ontology',
        templateUrl: '/partial/main/home/dashboard/create/manual/choose-ontology/choose-ontology.html'
    )
]