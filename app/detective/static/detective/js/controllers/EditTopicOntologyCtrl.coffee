class window.EditTopicOntologyCtrl
    @$inject: ['$scope', 'Page', '$rootScope', 'topic']
    constructor: (@scope, @Page, @rootScope, @topic)->
        @Page.title "Ontology Editor", no
        return unless @topic.ontology_as_json?
        # actions
        @scope.editModel                  = @editModel
        @scope.saveModel                  = @saveModel
        @scope.cancelModel                = @cancelModel
        @scope.removeFied                 = @removeFied
        @scope.accordionShouldBeDisabled  = @accordionShouldBeDisabled
        # data
        @scope.models        = @topic.ontology_as_json
        @scope.relationships = {}
        @scope.fieldTypes    = ["string", "url", "integer", "integerarray", "datetimestamp", "datetime", "date", "time", "boolean", "float"]
        for model in @scope.models
            for field in model.fields
                @scope.relationships[model.name] = [] unless @scope.relationships[model.name]?
                @scope.relationships[model.name].push field if field.type == "relationship"

    editModel: (model) =>
        @scope.editingModel = angular.copy(model)
        console.log "editModel", model

    saveModel: (model) =>
        model = @scope.editingModel
        idx_model_to_update = @scope.models.indexOf(_.find(@scope.models, ((m) -> model.name == m.name)))
        # update
        if idx_model_to_update > -1
            @scope.models[idx_model_to_update] = model
        @scope.editingModel = null

    cancelModel: (model) =>
        @scope.editingModel = null

    removeFied: (field) =>
        index = @scope.editingModel.fields.indexOf(field)
        if index > -1
            @scope.editingModel.fields.splice(index, 1) if @scope.editingModel.fields[index]?

    accordionShouldBeDisabled: (accordion_name) =>
        if @scope.editingModel?
            return true

angular.module('detective.controller').controller 'EditTopicOntologyCtrl', EditTopicOntologyCtrl

# EOF
