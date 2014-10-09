class window.AddSourcesModalCtrl
    # Injects dependencies
    @$inject: ['$scope', '$q', '$filter', '$modalInstance', 'Individual', 'UtilsFactory', "fields", "field", "meta"]
    constructor: (@scope, @q, @filter, @modalInstance, @Individual, @UtilsFactory,  @fields, @field, @meta)->
        @fields  = angular.copy @fields
        @sources = @fields.field_sources or []
        # @updateMasterSources()
        # Scope variables
        @scope.loading    = {}
        @scope.individual = @Individual
        # Description of the model's fields
        @scope.meta = @meta
        @scope.focus_new = true

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

        @scope.isLoading = => _.some(@scope.loading)

        # Description of the relationship (source, target, through model)
        @scope.fields = @fields

    close: (result=@sources)=>
        @modalInstance.close(result)

    save: (form, close=no)=>
        # if form is passed to the save function it has to be valid.
        return unless form.$valid if form?
        @close(@sources) if close

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

    getIndividualParams: =>
        id: @meta.id
        type: @meta.type

    getSourceParams: (source)=>
        _.extend @getIndividualParams(), { source_id: source.id }

    updateSource: (source)=>
        @scope.loading[source.id] = true
        @Individual.updateSource(@getSourceParams(source), source, =>
            @scope.loading[source.id] = false
        )
    deleteSource: (source)=>
        @scope.loading[source.id] = true

        @Individual.deleteSource(@getSourceParams(source), =>
                @scope.loading[source.id] = false
                @sources = _.reject @sources, _.matches
                    field: source.field
                    reference: source.reference
                @scope.focused = undefined
            , =>
                @scope.loading[source.id] = false
        )

    addSource: (source_text, form_text)=>
        new_source =
            reference: source_text
            field: @field.name

        @scope.loading['global'] = true
        @Individual.createSource(@getIndividualParams(), new_source, (source)=>
                @sources.push source
                @scope.focus_new = true
                @scope.loading['global'] = false
            , =>
                @scope.loading['global'] = false
        )

    getSources: => _.where @sources, field: @field.name

    getSourcesRefs: => _.map @getSources(), (s)-> s.reference

    # updateMasterSources: =>
    #     @master_sources = @getSources angular.copy @fields

    hasSources: =>
        sources = @getSources()
        (not _.isEmpty sources) and _.some sources, (e)-> e? and e.reference?

    isSourceURLValid: (source)=>
        return false unless source?
        @UtilsFactory.isValidURL(source.reference)



angular.module('detective.controller').controller 'addSourcesModalCtrl', AddSourcesModalCtrl