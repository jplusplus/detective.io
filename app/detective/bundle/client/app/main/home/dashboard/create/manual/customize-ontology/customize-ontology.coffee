angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('user-topic-create.manual.customize-ontology',
        controller: EditTopicOntologyCtrl
        templateUrl: '/partial/main/home/dashboard/create/manual/customize-ontology/customize-ontology.html'
    )
]