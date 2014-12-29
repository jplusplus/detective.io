angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('user-topic-edit.customize-ontology',
        controller: EditTopicOntologyCtrl
        url: "structure/"
        templateUrl: '/partial/main/home/dashboard/create/customize-ontology/customize-ontology.html'
    )
]