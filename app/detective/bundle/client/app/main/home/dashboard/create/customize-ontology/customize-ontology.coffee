angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('user-topic-create.customize-ontology',
        controller: EditTopicOntologyCtrl
        templateUrl: '/partial/main/home/dashboard/create/customize-ontology/customize-ontology.html'
    )
]