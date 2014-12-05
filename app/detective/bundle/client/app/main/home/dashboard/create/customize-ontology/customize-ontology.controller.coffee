class window.EditTopicOntologyCtrl
    @$inject: ['$scope', 'Page', '$rootScope', 'TopicsFactory', '$modal']
    constructor: (@scope, @Page, @rootScope,  @TopicsFactory, @modal)->
        # Scope methods
        @scope.hasSelectedModel         = @hasSelectedModel
        @scope.hasSelectedRelationship  = @hasSelectedRelationship
        @scope.startEditingModel        = @startEditingModel
        @scope.startEditingRelationship = @startEditingRelationship
        @scope.startOver                = @startOver
        @scope.editModel                = @editModel
        @scope.editRelationship         = @editRelationship
        @scope.addModel                 = @addModel
        @scope.addRelationship          = @addRelationship
        @scope.relationships            = @getAllRelationships
        @scope.getModel                 = @getModel
        @scope.hasRelationships         = @hasRelationships
        @scope.removeModel              = @removeModel
        @scope.removeRelationship       = @removeRelationship
        # Initialize variables
        do @startOver
        # List of current model
        @scope.models                   = @scope.selected_skeleton.ontology or []

    # Shortcuts
    hasSelectedModel        : => @scope.selectedModel?
    hasSelectedRelationship : => @scope.selectedRelationship?
    startEditingModel       : (model)=> @scope.selectedModel = model
    startEditingRelationship: (relationship)=> @scope.selectedRelationship = relationship
    getModel                : (name)=> _.find @scope.models, name: name

    startOver: =>
        # Panels display
        @scope.addingModel         = no
        @scope.addingRelationship  = no
        @scope.editingModel        = no
        @scope.editingRelationship = no
        # Edited objects
        @scope.newModel            = {}
        @scope.newRelationship     = {}
        @scope.selectedModel       = null
        @scope.selectedRelationship= null

    addModel: (model)=>
        @scope.models.push angular.copy(model)
        # Empty given model
        delete @scope.newModel[f] for f of @scope.newModel
        do @startOver

    editModel: (model)=>
        old_name = @scope.selectedModel.name
        new_name = model.name
        angular.extend @scope.selectedModel, model
        # The name changed?
        # We must change every relationships using the old model name.
        if old_name isnt new_name
            # For each model fields...
            angular.forEach @scope.models, (m)=>
                angular.forEach m.fields, (field)=>
                    # The given field is a relationship to the old_model
                    if field.related_model is old_name
                        # We edit the value in the model array (references won't work, dunno why)
                        field.related_model = new_name
        do @startOver

    removeModel: (model)=>
        modalInstance = @modal.open
            templateUrl: '/partial/main/home/dashboard/create/customize-ontology/remove-model/remove-model.html' 
            controller: ($scope, $modalInstance)-> 
                $scope.model = model                
                $scope.ok = -> do $modalInstance.close
                $scope.cancel = -> $modalInstance.dismiss 'cancel'
        # Removing approved
        modalInstance.result.then =>
            # Look into the other models
            for m, model_index in @scope.models 
                # Remove every field related to this model
                m.fields = _.filter m.fields, (field)-> field.related_model isnt model.name                        
            @scope.models = _.without @scope.models, model
            do @startOver

    addRelationship: (relationship)=>
        model = _.find @scope.models, name: relationship.model
        model.fields.push relationship
        do @startOver

    editRelationship: (relationship)=>
        model    = @getModel relationship.model
        angular.extend @scope.selectedRelationship, relationship
        do @startOver

    removeRelationship: (relationship)=>
        modalInstance = @modal.open
            templateUrl: '/partial/main/home/dashboard/create/customize-ontology/remove-relationship/remove-relationship.html' 
            controller: ($scope, $modalInstance)=> 
                $scope.relationship = relationship                
                $scope.getModel = @getModel                
                $scope.ok = -> do $modalInstance.close
                $scope.cancel = -> $modalInstance.dismiss 'cancel'
        # Removing approved
        modalInstance.result.then =>
            model = @getModel relationship.model
            model.fields = _.without model.fields, relationship
            do @startOver

    getAllRelationships: =>
        relationships = {}
        for model in @scope.models
            for field in model.fields
                relationships[model.name] = [] unless relationships[model.name]?
                relationships[model.name].push field if field.type == "relationship"
        relationships

    hasRelationships: =>
        relationships = do @getAllRelationships
        !! _.keys(relationships).length


angular.module('detective.controller').controller 'editTopicOntologyCtrl', EditTopicOntologyCtrl
# EOF
