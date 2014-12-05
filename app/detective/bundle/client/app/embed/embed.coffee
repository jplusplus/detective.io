angular.module('detective.config').config [
    "$stateProvider", "$urlRouterProvider", "$locationProvider",
    ($stateProvider, $urlRouterProvider, $locationProvider)->
        # HTML5 Mode yeah!
        $locationProvider.html5Mode true
        # Not found URL
        $urlRouterProvider.otherwise("/embed/");        
        # ui-router configuration
        $stateProvider.state('entity',
            url: '/embed/:username/:topic/:type/:id/'
            controller: ['$scope', '$stateParams', 'individual', 'graphnodes', 'topic', 'Page'
                ($scope, $stateParams, individual, graphnodes, topic, Page)->
                    $scope.topic      = topic
                    $scope.individual = individual
                    $scope.graphnodes = graphnodes
                    $scope.link = "/#{$stateParams.username}/#{$stateParams.topic}/#{$stateParams.type}/#{$stateParams.id}/"
                    # Update page title
                    Page.title( $scope.individual.name or "Unkown" )
            ]
            resolve:
                topic: UserTopicCtrl.resolve.topic
                forms: UserTopicCtrl.resolve.forms
                individual: UserTopicCtrl.resolve.individual
                graphnodes: [ 'Individual', '$stateParams', (Individual, $stateParams)->                    
                    Individual.graph($stateParams).$promise
                ]
        )

]