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
        @scope.cancel           = @close
        @scope.save             = @save
        @scope.updateSource     = @updateSource
        @scope.addSource        = @addSource
        @scope.deleteSource     = @deleteSource
        @scope.getSources       = @getSources
        @scope.getSourcesRefs   = @getSourcesRefs
        @scope.submit           = @submit
        @scope.isSourceURLValid = @isSourceURLValid
        @scope.isFieldSource    = (source)=> source.field is @field.name

        # Description of the relationship (source, target, through model)
        @scope.fields = @fields

    close: (result)=>
        console.log 'AddSourcesModalCtrl.close'
        @modalInstance.close(result)


    save: (form, close=no)=>
        if form?
            return unless form.$valid
        @scope.loading = yes
        @meta.updating[@field.name] = true
        data  =
            field_sources: @cleanSources()
        params  =
            id:   @meta.id
            type: @meta.type

        # Update individual sources
        promise = @Individual.update(params, data).$promise

        promise.then (data)=>
            @scope.loading = no
            @updateMasterSources()
            @scope.focus_add = true

        @close(promise) if close


    getSources: (fields=@fields) => _.where fields.field_sources, field: @field.name

    getSourcesRefs: ()=> _.map @getSources(), (s)-> s.reference

    addSource: (value)=>
        @scope.focus_add = false
        @fields.field_sources.push
            reference: value
            field: @field.name
            focus: true

    isSaveOrCancelBtn: (el)=>
        /^(save|cancel)/.test ($(el).attr('ng-click') or '')

    cleanSources: =>
        _.map @fields.field_sources, (v)-> _.omit v, 'focus'

    updateSource: (source, form, $index, $event)=>
        return unless form.$valid
        # workaround to avoid loading when we click on save/or cancel
        return if @isSaveOrCancelBtn($event.relatedTarget)
        master_source = @master_sources[$index]
        has_changed   = not (source? and master_source?) or source.reference != master_source.reference
        if has_changed
            @save(form)

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

    submit: (form)=>
        @save(form)


angular.module('detective.controller').controller 'addSourcesModalCtrl', AddSourcesModalCtrl