class window.EditTopicOntologyCtrl
    @$inject: ['$scope', 'Page', '$rootScope', 'topic']
    constructor: (@scope, @Page, @rootScope, @topic)->
        @Page.title "Ontology Editor", no
        if @topic.ontology_as_json?
            @scope.fields = @topic.ontology_as_json
            console.log @scope.fields

            jsPlumb.ready ->
                jsPlumb.makeSource $(".item"),
                    connector: "StateMachine"
                jsPlumb.makeTarget $(".item"),
                    anchor: "Continuous"

angular.module('detective.controller').controller 'EditTopicOntologyCtrl', EditTopicOntologyCtrl