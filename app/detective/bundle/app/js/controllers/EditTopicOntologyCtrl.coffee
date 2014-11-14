class window.EditTopicOntologyCtrl
    @$inject: ['$scope', 'Page', '$rootScope', 'TopicsFactory']
    constructor: (@scope, @Page, @rootScope,  @TopicsFactory)->
        # Scope methods
        @scope.addModel            = @addModel
        @scope.hasSelectedModel    = @hasSelectedModel
        @scope.startEditingModel   = @startEditingModel
        @scope.editModel           = @editModel
        @scope.relationships       = @getAllRelationships
        # Panels display
        @scope.addingModel         = no
        @scope.addingRelationship  = no
        @scope.editingModel        = yes
        @scope.editingRelationship = no
        # List of current model
        @scope.models              = @scope.selected_skeleton.ontology or []
        # New model object
        @scope.newModel            = {}
        @scope.selectedModel       = @scope.models[0]

    addModel: (model)=>
        @scope.models.push angular.copy(model)
        # Empty given model
        delete @scope.newModel[f] for f of @scope.newModel
        @scope.addingModel = no

    hasSelectedModel: => @scope.selectedModel?

    startEditingModel: (model)=> @scope.selectedModel = model

    editModel: (model)=>
        old_name = @scope.selectedModel.name
        new_name = model.name
        # Edit the right model object using the saved index
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
        # Start over
        @scope.selectedModel      = null
        @scope.editingModel       = no


    addRelationship: =>
        new_relationship_field = {
            fields        : []
            help_text     : ""
            name          : @slugify(@scope.newRelationship.name)
            verbose_name  : @scope.newRelationship.name
            related_name  : @slugify(@scope.newRelationship.reverseName)
            related_model : @scope.newRelationship.and
            rules         : {search_terms: []}
            type          : "relationship"
        }
        # update the model
        @getModelByName(@scope.newRelationship.between).fields.push(new_relationship_field)
        @scope.newRelationship = {}

    getAllRelationships: =>
        relationships = {}
        for model in @scope.models
            for field in model.fields
                relationships[model.name] = [] unless relationships[model.name]?
                relationships[model.name].push field if field.type == "relationship"
        relationships

    # -----------------------------------------------------------------------------
    #    Utils
    # -----------------------------------------------------------------------------
    saveOntology: =>
        # @TopicsFactory.update({id: @topic.id}, {ontology_as_json:@scope.models})



angular.module('detective.controller').controller 'editTopicOntologyCtrl', EditTopicOntologyCtrl
# EOF
