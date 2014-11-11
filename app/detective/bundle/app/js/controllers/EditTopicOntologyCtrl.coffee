class window.EditTopicOntologyCtrl
    @$inject: ['$scope', 'Page', '$rootScope', 'TopicsFactory']
    constructor: (@scope, @Page, @rootScope,  @TopicsFactory)->
        # actions #1: add a new model
        @scope.addNewModel                         = @addNewModel
        @scope.modelNameAlreadyExist               = @modelNameAlreadyExist
        # actions #2: add a new relationship
        @scope.addNewRelationship                  = @addNewRelationship
        @scope.relationshipNameAlreadyExist        = @relationshipNameAlreadyExist
        @scope.relationshipReverseNameAlreadyExist = @relationshipReverseNameAlreadyExist
        # actions #3: edit a model
        @scope.editModel                           = @editModel
        @scope.saveModel                           = @saveModel
        @scope.cancelModel                         = @cancelModel
        @scope.removeModelField                    = @removeModelField
        @scope.addModelField                       = @addModelField
        # actions #4: edit a relationship
        @scope.editRelationship                    = @editRelationship
        @scope.saveRelationship                    = @saveRelationship
        @scope.cancelRelationship                  = @cancelRelationship
        @scope.removeRelationshipField             = @removeRelationshipField
        @scope.addRelationshipField                = @addRelationshipField
        # methodes
        @scope.accordionShouldBeDisabled           = @accordionShouldBeDisabled
        @scope.isModelUnchanged                    = @isModelUnchanged
        @scope.isRelationshipUnchanged             = @isRelationshipUnchanged
        # data
        @scope.models              = @scope.selected_skeleton.ontology or []
        @scope.fieldTypes          = ["string", "url", "integer", "integerarray", "datetimestamp", "datetime", "date", "time", "boolean", "float"]
        @scope.newModel            = {}
        @scope.newRelationship     = {}
        @scope.editingModel        = null
        @scope.editingRelationship = null
        @scope.relationships       = =>
            relationships = {}
            for model in @scope.models
                for field in model.fields
                    relationships[model.name] = [] unless relationships[model.name]?
                    relationships[model.name].push field if field.type == "relationship"
            return relationships
        # watch editingModel to update the name if doesn't exist
        @scope.$watch("editingModel", =>
            return unless @scope.editingModel?
            model_base = @getModelByName(@scope.editingModel.name)
            already_checked = {} # prevent new model with existing name (doublon) to be skiped
            for field in @scope.editingModel.fields
                field_base = null
                if field.name? and not already_checked[field.name]?
                    field_base = @getFieldfromModel(field.name, model_base)
                    if field_base?
                        already_checked[field_base.name] = true
                if not field_base?
                    field.name = @slugify(field.verbose_name)
        , true)

    # -----------------------------------------------------------------------------
    #    #1 ADD A NEW MODEL
    # -----------------------------------------------------------------------------
    addNewModel: =>
        new_model =
            fields              : [{name:"name", verbose_name:"Name", type:"string"}]
            name                : @slugify(@scope.newModel.name)
            verbose_name        : @scope.newModel.name
            verbose_name_plural : @scope.newModel.namePlural
            help_text           : @scope.newModel.helpText
        @scope.models.push(new_model)
        @saveOntology()
        @scope.newModel = {}

    modelNameAlreadyExist: =>
        return no unless @scope.newModel.name?
        @scope.newModel.name = @slugify(@scope.newModel.name)
        for model in @scope.models
            if model.name == @scope.newModel.name
                return yes
        no

    # -----------------------------------------------------------------------------
    #    #2 ADD A NEW RELATIONSHIP
    # -----------------------------------------------------------------------------
    addNewRelationship: =>
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
        @saveOntology()
        @scope.newRelationship = {}

    relationshipNameAlreadyExist: =>
        return no unless @scope.newRelationship.between? and @scope.newRelationship.name?
        for field in @getModelByName(@scope.newRelationship.between).fields
            if field.name == @slugify(@scope.newRelationship.name)
                return yes
        return no

    relationshipReverseNameAlreadyExist: =>
        return no unless @scope.newRelationship.between? and @scope.newRelationship.reverseName?
        for field in @getModelByName(@scope.newRelationship.between).fields
            if field.related_name == @slugify(@scope.newRelationship.reverseName)
                return yes
        return no

    # -----------------------------------------------------------------------------
    #    #3 EDIT A MODEL
    # -----------------------------------------------------------------------------
    editModel: (model) =>
        @scope.editingModel = angular.copy(model)

    saveModel:  =>
        model = @scope.editingModel
        idx_model_to_update = @scope.models.indexOf(_.find(@scope.models, ((m) -> model.name == m.name)))
        # update
        if idx_model_to_update > -1
            @scope.models[idx_model_to_update] = model
            @saveOntology()
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
    #    #4 EDIT A RELATIONSHIP
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
            @saveOntology()
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
    saveOntology: =>
        # @TopicsFactory.update({id: @topic.id}, {ontology_as_json:@scope.models})

    getModelByName: (name) =>
        return null unless name?
        idx_model = @scope.models.indexOf(_.find(@scope.models, ((m) => name == m.name)))
        if idx_model > -1
            return @scope.models[idx_model]
        return null

    getFieldfromModel: (field_name, model) =>
        for field in model.fields
            if field.name == field_name
                return field
        return null

    accordionShouldBeDisabled: (accordion_name) =>
        if @scope.editingModel? or @scope.editingRelationship?
            return true

    slugify: (name) =>
        return "" unless name?
        name
            .toLowerCase()
            .replace(/\ /g, '_')
            .replace(/[^\w-]+/g, '')

angular.module('detective.controller').controller 'editTopicOntologyCtrl', EditTopicOntologyCtrl
# EOF
