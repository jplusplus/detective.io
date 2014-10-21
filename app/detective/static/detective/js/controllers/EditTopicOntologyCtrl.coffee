class window.EditTopicOntologyCtrl
    @$inject: ['$scope', 'Page', '$rootScope', 'topic']
    constructor: (@scope, @Page, @rootScope, @topic)->
        @Page.title "Ontology Editor", no
        return unless @topic.ontology_as_json?
        # actions: add a new model
        @scope.addNewModel                = @addNewModel
        @scope.addNewRelationship         = @addNewRelationship
        # actions: edit a model
        @scope.editModel                  = @editModel
        @scope.saveModel                  = @saveModel
        @scope.cancelModel                = @cancelModel
        @scope.removeModelField           = @removeModelField
        @scope.addModelField              = @addModelField
        # actions: edit a relationship
        @scope.editRelationship           = @editRelationship
        @scope.saveRelationship           = @saveRelationship
        @scope.cancelRelationship         = @cancelRelationship
        @scope.removeRelationshipField    = @removeRelationshipField
        @scope.addRelationshipField       = @addRelationshipField
        # methodes
        @scope.accordionShouldBeDisabled  = @accordionShouldBeDisabled
        @scope.isModelUnchanged           = @isModelUnchanged
        @scope.isRelationshipUnchanged    = @isRelationshipUnchanged
        # data
        @scope.models              = @topic.ontology_as_json
        @scope.fieldTypes          = ["string", "url", "integer", "integerarray", "datetimestamp", "datetime", "date", "time", "boolean", "float"]
        @scope.newModel            = {}
        @scope.newRelationship     = {}
        @scope.editingModel        = null
        @scope.editingRelationship = null

        @scope.relationships = =>
            relationships = {}
            for model in @scope.models
                for field in model.fields
                    relationships[model.name] = [] unless relationships[model.name]?
                    relationships[model.name].push field if field.type == "relationship"
            return relationships

    # -----------------------------------------------------------------------------
    #    ADD A NEW MODEL
    # -----------------------------------------------------------------------------
    addNewModel: =>
        new_model =
            fields              : [{name:"name", verbose_name:"Name", type:"string"}]
            name                : @scope.newModel.name # TODO: slugify
            verbose_name        : @scope.newModel.name
            verbose_name_plural : @scope.newModel.namePlural
            help_text           : @scope.newModel.helpText
        @scope.models.push(new_model)
        @scope.newModel = {}

    # -----------------------------------------------------------------------------
    #    ADD A NEW RELATIONSHIP
    # -----------------------------------------------------------------------------
    addNewRelationship: =>
        new_relationship_field = {
            fields        : []
            help_text     : ""
            name          : @scope.newRelationship.name # TODO: slugify
            verbose_name  : @scope.newRelationship.name
            related_name  : @scope.newRelationship.reverseName
            related_model : @scope.newRelationship.and
            rules         : {search_terms: []}
            type          : "relationship"

        }
        idx_model_to_update = @scope.models.indexOf(_.find(@scope.models, ((m) => @scope.newRelationship.between == m.name)))
        # update the model
        @scope.models[idx_model_to_update].fields.push(new_relationship_field)
        @scope.newRelationship = {}

    # -----------------------------------------------------------------------------
    #    EDIT A MODEL
    # -----------------------------------------------------------------------------
    editModel: (model) =>
        @scope.editingModel = angular.copy(model)

    saveModel:  =>
        model = @scope.editingModel
        # create the name from the verbose name if doesn't exist
        for field in model.fields
            if not field.name?
                # slugify
                field.name = field.verbose_name
                .toLowerCase()
                .replace(/\ /g, '-')
                .replace(/[^\w-]+/g, '')
                # TODO : check if doesn't exist
        idx_model_to_update = @scope.models.indexOf(_.find(@scope.models, ((m) -> model.name == m.name)))
        # update
        if idx_model_to_update > -1
            @scope.models[idx_model_to_update] = model
        @scope.editingModel = null

    cancelModel: =>
        @scope.editingModel = null

    addModelField: =>
        @scope.editingModel.fields.push({})

    removeModelField: (field) =>
        index = @scope.editingModel.fields.indexOf(field)
        if index > -1
            @scope.editingModel.fields.splice(index, 1) if @scope.editingModel.fields[index]?

    isModelUnchanged: =>
        idx_model_to_update = @scope.models.indexOf(_.find(@scope.models, ((m) => @scope.editingModel.name == m.name)))
        angular.equals(@scope.editingModel, @scope.models[idx_model_to_update])

    # -----------------------------------------------------------------------------
    #    EDIT A RELATIONSHIP
    # -----------------------------------------------------------------------------
    editRelationship: (model, relationship) =>
        @scope.editingRelationship      = angular.copy(relationship)
        @scope.editingRelationshipModel = angular.copy(model)

    getRelationshipToUpdate: =>
        idx_model_to_update        = @scope.models.indexOf(_.find(@scope.models, ((m) => @scope.editingRelationshipModel.name == m.name)))
        idx_relationship_to_update = @scope.models[idx_model_to_update].fields.indexOf(_.find(@scope.models[idx_model_to_update].fields, ((f) => @scope.editingRelationship.name == f.name)))
        if idx_model_to_update > -1 and idx_relationship_to_update > -1
            return @scope.models[idx_model_to_update].fields[idx_relationship_to_update]

    saveRelationship:  =>
        idx_model_to_update        = @scope.models.indexOf(_.find(@scope.models, ((m) => @scope.editingRelationshipModel.name == m.name)))
        idx_relationship_to_update = @scope.models[idx_model_to_update].fields.indexOf(_.find(@scope.models[idx_model_to_update].fields, ((f) => @scope.editingRelationship.name == f.name)))
        # update
        if idx_model_to_update > -1 and idx_relationship_to_update > -1
            @scope.models[idx_model_to_update].fields[idx_relationship_to_update] = @scope.editingRelationship
        @scope.editingRelationship      = null
        @scope.editingRelationshipModel = null

    cancelRelationship: =>
        @scope.editingRelationship      = null
        @scope.editingRelationshipModel = null

    removeRelationshipField: (field) =>
        index = @scope.editingRelationship.fields.indexOf(field)
        if index > -1
            @scope.editingRelationship.fields.splice(index, 1) if @scope.editingRelationship.fields[index]?

    addRelationshipField: =>
        if not @scope.editingRelationship.fields?
            @scope.editingRelationship.fields = []
        @scope.editingRelationship.fields.push({})

    isRelationshipUnchanged: =>
        idx_model_to_update        = @scope.models.indexOf(_.find(@scope.models, ((m) => @scope.editingRelationshipModel.name == m.name)))
        idx_relationship_to_update = @scope.models[idx_model_to_update].fields.indexOf(_.find(@scope.models[idx_model_to_update].fields, ((f) => @scope.editingRelationship.name == f.name)))
        if idx_model_to_update > -1 and idx_relationship_to_update > -1
            angular.equals(@scope.editingRelationship, @scope.models[idx_model_to_update].fields[idx_relationship_to_update])
    
    # -----------------------------------------------------------------------------
    #    Utils
    # -----------------------------------------------------------------------------
    accordionShouldBeDisabled: (accordion_name) =>
        if @scope.editingModel? or @scope.editingRelationship?
            return true


angular.module('detective.controller').controller 'EditTopicOntologyCtrl', EditTopicOntologyCtrl

# EOF
