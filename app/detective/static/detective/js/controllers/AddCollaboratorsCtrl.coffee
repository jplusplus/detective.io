class AddCollaboratorsCtrl
    # Injects dependancies
    @$inject: ['$scope', '$stateParams', '$state', 'Common', 'Page', 'topic']
    constructor: (@scope,  @stateParams, @state, @Common, @Page, topic)->
        @scope.topic = topic
        @Page.loading no


    @resolve:
        topic: ["Common", "$stateParams", (Common, $stateParams)->
            Common.cachedGet(type: "topic", id: $stateParams.topic).$promise
        ]

angular.module('detective.controller').controller 'addCollaboratorsCtrl', AddCollaboratorsCtrl