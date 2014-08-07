class AddCollaboratorsCtrl
    # Injects dependancies
    @$inject: ['$scope', '$stateParams', '$state', 'Topic', 'Page', 'topic']
    constructor: (@scope,  @stateParams, @state, @Topic, @Page, @topic)->
        @Page.loading no
        @Page.title "Add new collaborators"
        @scope.topic = @topic
        # Transform search result
        @scope.prepareSearch = (objects=[])->
            # Fetchs and returns the objects list
            for object in objects
                # Create a new field "name" using the "username"
                object["name"] = object["username"]
                # Return the updated object
                object

        @scope.$watch "collaborator", (newVal, oldVal)=>
            if typeof newVal is typeof {}
                @scope.collaborator_name = newVal.username

        # Send an invitation to the given person
        @scope.invite = ()=>
            collaborator = @scope.collaborator_name
            @scope.loading = yes
            @scope.invited = null

            @Topic.invite({id: @topic.id}, {collaborator: collaborator}, =>
                @scope.loading = no
                # Success notification
                @scope.invited = collaborator
            # Error
            , => @scope.loading = no)



    @resolve:
        topic: ["Common", "$stateParams", (Common, $stateParams)->
            Common.cachedGet(type: "topic", id: $stateParams.topic).$promise
        ]

angular.module('detective.controller').controller 'addCollaboratorsCtrl', AddCollaboratorsCtrl