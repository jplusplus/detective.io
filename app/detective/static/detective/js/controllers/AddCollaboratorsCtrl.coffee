class window.AddCollaboratorsCtrl
    # Injects dependancies
    @$inject: ['$scope', '$stateParams', '$state', 'Topic', 'Page', 'topic', 'collaborators', 'User']
    constructor: (@scope,  @stateParams, @state, @Topic, @Page, @topic, collaborators, @User)->
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
                @scope.collaborator_name = ""
                do @updateCollaborators
            # Error
            , => @scope.loading = no)

        ##
        # Collaborators
        @collaborator_loading = []
        @scope.collaborators = collaborators
        @scope.orderCollaborators = @orderCollaborators
        @scope.isYou = @isYou
        @scope.isOwner = @isOwner
        @scope.isLoading = @isLoading
        @scope.changePermission = @changePermission
        @scope.removeCollaborator = @removeCollaborator
        #
        ##

    orderCollaborators: (user) =>
        if user.id is @topic.author.id then 1 else 3

    isYou: (user) =>
        user.id is @User.id

    isOwner: (user) =>
        user.id is @topic.author.id

    isLoading: (user) =>
        user.id in @collaborator_loading

    changePermission: (user) =>
        @setCollaboratorLoading user

    setCollaboratorLoading: (user) =>
        if user.id not in @collaborator_loading
            @collaborator_loading.push user.id

    unsetCollaboratorLoading: (user) =>
        if user.id in @collaborator_loading
            @collaborator_loading = @collaborator_loading.splice (@collaborator_loading.indexOf user.id), 1

    removeCollaborator: (user) =>
        if (confirm "Are you sure?")
            @scope.loading = yes
            @Topic.leave { id : @topic.id }, { collaborator : user.id }, =>
                @scope.loading = no
                do @updateCollaborators

    updateCollaborators: =>
        @scope.loading = yes
        (@Topic.collaborators { id : @topic.id }).$promise.then (data) =>
            @scope.loading = no
            @scope.collaborators = data

    @resolve:
        collaborators: ["Topic", "topic", (Topic, topic) ->
            Topic.collaborators(id: topic.id).$promise
        ]

angular.module('detective.controller').controller 'addCollaboratorsCtrl', AddCollaboratorsCtrl