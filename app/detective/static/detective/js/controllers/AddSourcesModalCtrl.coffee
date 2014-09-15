class window.AddSourcesModalCtrl
    # Injects dependencies
    @$inject: ['$scope', '$q', '$modalInstance', 'Individual', 'UtilsFactory', "fields", "field", "meta"]
    constructor: (@scope, @q, @modalInstance, @Individual, @UtilsFactory,  @fields, @field, @meta)->
        @fields = angular.copy @fields
        @updateMasterSources()
        # Scope variables
        @scope.loading    = no
        @scope.individual = @Individual
        # workout to focus last field of sources form
        @scope.focus_add   = yes
        @scope.field_value = @fields[field.name]
        # Description of the model's fields
        @scope.meta = @meta

        # Scope functions
        # Cancel button just closes the modal
        @scope.cancel       = @close
        @scope.save         = @save
        @scope.updateSource = @updateSource
        @scope.addSource    = @addSource
        @scope.deleteSource = @deleteSource

        # Description of the relationship (source, target, through model)
        @scope.fields = @fields
        @scope.isSourceURLValid = @isSourceURLValid
        @scope.isFieldSource = (source)=> source.field == @field.name

    close: (result=@fields)=>
        @modalInstance.close(result)

    save: (close=no)=>
        @scope.loading = yes
        @meta.updating[@field.name] = yes
        sources = angular.copy @fields.field_sources
        data    =
            field_sources: _.map sources, (v)-> _.omit v, 'focus'
        params  =
            id:   @meta.id
            type: @meta.type

        # Update individual sources
        promise = @Individual.update(params, data).$promise

        promise.then (data)=>
            @scope.loading = no
            @updateMasterSources()
            @scope.$broadcast "individual:updated", data

        @close(promise) if close


    getSources: (fields=@fields) => _.where fields.field_sources, field: @field.name

    getSourcesRefs: (field)=> _.map @getSources(), (s)-> s.reference

    addSource: (form, value)=>
        return unless form.$valid

        @fields.field_sources.push
            reference: value
            field: @field.name
            focus: true

    isSaveOrCancelBtn: (el)=>
        /^(save|cancel)/.test ($(el).attr('ng-click') or '')

    updateSource: (source, $index, $event)=>
        # workaround to avoid loading when we click on save/or cancel
        return if @isSaveOrCancelBtn($event.relatedTarget)

        master_source = @master_sources[$index]
        has_changed   = not (source? and master_source?) or source.reference != master_source.reference
        if has_changed
            @save()

    updateMasterSources: =>
        @master_sources = @getSources angular.copy @fields

    deleteSource: (source, $event)=>
        @fields.field_sources = _.reject @fields.field_sources, _.matches
                field: source.field
                reference: source.reference
        @save()

    hasSources: =>
        sources = @getSources()
        (not _.isEmpty sources) and _.some sources, (e)-> e? and e.reference?

    isSourceURLValid: (source)=>
        return false unless source?
        @UtilsFactory.isValidURL(source.reference)



angular.module('detective.controller').controller 'addSourcesModalCtrl', AddSourcesModalCtrl