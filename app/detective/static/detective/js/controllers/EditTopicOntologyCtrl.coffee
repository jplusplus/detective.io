class window.EditTopicOntologyCtrl
    @$inject: ['$scope', 'Page', '$rootScope', 'topic']
    constructor: (@scope, @Page, @rootScope, @topic)->
        super
        @Page.title "POUET", no
        console.log "pouet"

angular.module('detective.controller').controller 'EditTopicOntologyCtrl', EditTopicOntologyCtrl