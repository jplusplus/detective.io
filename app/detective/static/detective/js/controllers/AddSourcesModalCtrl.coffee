class window.AddSourcesModalCtrl
    # Injects dependencies
    @$inject: ['$scope', '$q', '$filter', '$modalInstance', 'Individual', 'UtilsFactory', "fields", "field", "meta"]
    constructor: (@scope, @q, @filter, @modalInstance, @Individual, @UtilsFactory,  @fields, @field, @meta)->
        @fields = angular.copy @fields
        @updateMasterSources()
        # Scope variables
        @scope.loading    = no
        @scope.individual = @Individual
        # Description of the model's fields
        @scope.meta = @meta

        # Scope functions
        # Cancel button just closes the modal
        @scope.cancel           = @close
        @scope.save             = @save
        @scope.updateSource     = @updateSource
        @scope.addSource        = @addSource
        @scope.deleteSource     = @deleteSource
        @scope.getFieldValue    = @getFieldValue
        @scope.getSources       = @getSources
        @scope.getSourcesRefs   = @getSourcesRefs
        @scope.isSourceURLValid = @isSourceURLValid

        # Description of the relationship (source, target, through model)
        @scope.fields = @fields

    close: (result=@fields)=>
        @modalInstance.close(result)

    save: (form, close=no)=>
        # if form is passed to the save function it has to be valid.
        return unless form.$valid if form?
        @scope.focused = undefined
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
            @updateMasterSources()
            @scope.loading = no
            @meta.updating[@field.name] = false

        @close(promise) if close

    isFieldRich: (field)=>
        field.rules.is_rich or no

    getFieldValue: ()=>
        field_value = @fields[@field.name]
        # field type switch
        switch @field.type
            when 'CharField'
                if @isFieldRich(@field)
                    field_value = @field.verbose_name
            when 'DateTimeField'
                format  = "shortDate"
                field_value =  @filter("date")(field_value, format)
            when 'Relationship'
                field_value = @field.verbose_name

        unless field_value?
            field_value = @field.verbose_name

        field_value


    getSources: (fields=@fields) => _.where fields.field_sources, field: @field.name

    getSourcesRefs: ()=> _.map @getSources(), (s)-> s.reference

    addSource: (value)=>
        @fields.field_sources.push
            reference: value
            field: @field.name

        @scope.focused = value

    cleanSources: =>
        _.map @fields.field_sources, (v)-> _.omit v, 'focus'

    # isSaveOrCancelBtn: (el)=>
    #     /^(save|cancel)/.test ($(el).attr('ng-click') or '')

    # updateSource: (source, form, $index, $event)=>
    #     # if we're already saving we don't need to update sources
    #     return if @scope.loading
    #     return unless form.$valid
    #     # workaround to avoid loading when we click on save/or cancel
    #     return if @isSaveOrCancelBtn($event.relatedTarget)
    #     master_source = @master_sources[$index]
    #     has_changed   = not (source? and master_source?) or source.reference != master_source.reference
    #     @save(form) if has_changed

    updateMasterSources: =>
        @master_sources = @getSources angular.copy @fields

    deleteSource: (form, source, $event)=>
        @fields.field_sources = _.reject @fields.field_sources, _.matches
                field: source.field
                reference: source.reference
        @scope.focused = undefined
        # @save(form)

    hasSources: =>
        sources = @getSources()
        (not _.isEmpty sources) and _.some sources, (e)-> e? and e.reference?

    isSourceURLValid: (source)=>
        return false unless source?
        @UtilsFactory.isValidURL(source.reference)


angular.module('detective.controller').controller 'addSourcesModalCtrl', AddSourcesModalCtrl