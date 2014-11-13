class window.EditTopicOntologyCtrl
    @$inject: ['$scope', 'Page', '$rootScope', 'TopicsFactory']
    constructor: (@scope, @Page, @rootScope,  @TopicsFactory)->
        # Scope methods
        @scope.addModel  = @addModel
        @scope.editModel = @editModel
        # Panels display
        @scope.addingModel         = no
        @scope.addingRelationship  = no
        @scope.editingModel        = yes
        @scope.editingRelationship = no
        # List of current model
        @scope.models              = @scope.selected_skeleton.ontology or []
        # New model object
        @scope.newModel = {}
        @scope.selectedModel = @scope.models[0]
        # List of current relationships
        @scope.relationships       = =>
            relationships = {}
            for model in @scope.models
                for field in model.fields
                    relationships[model.name] = [] unless relationships[model.name]?
                    relationships[model.name].push field if field.type == "relationship"
            relationships

    addModel: (model)=>
        @scope.models.push angular.copy(@scope.newModel)
        # Empty given model
        delete @scope.newModel[f] for f of @scope.newModel
        @scope.addingModel = no


    editModel: (model, master)=>
        angular.extend master, model
        # Start over
        @scope.selectedModel = {}
        @scope.editingModel = no


    # -----------------------------------------------------------------------------
    #    #2 ADD A NEW RELATIONSHIP
    # -----------------------------------------------------------------------------
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

    # -----------------------------------------------------------------------------
    #    Utils
    # -----------------------------------------------------------------------------
    saveOntology: =>
        # @TopicsFactory.update({id: @topic.id}, {ontology_as_json:@scope.models})



angular.module('detective.controller').controller 'editTopicOntologyCtrl', EditTopicOntologyCtrl
# EOF
