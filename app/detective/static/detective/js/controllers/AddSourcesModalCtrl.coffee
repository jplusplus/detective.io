class window.AddSourcesModalCtrl
    # Injects dependencies
    @$inject: ['$scope', '$q', '$filter', '$modalInstance', 'Individual', 'UtilsFactory',  'constants.events', "fields", "field", "meta"]
    constructor: (@scope, @q, @filter, @modalInstance, @Individual, @UtilsFactory, @EVENTS, @fields, @field, @meta)->
        @fields  = angular.copy @fields
        @sources = @fields.field_sources or []
        @updateMasterSources()
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

    save: (new_source, close=no)=>
        if new_source?
            res = @addSource(new_source)
            if res? and typeof res != typeof true
                res.$promise.then =>
                    @close(@sources) if close
            else
                @close(@sources) if close
        else
            # if form is passed to the save function it has to be valid.
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

    hasChanged: (source)=>
        master_source = _.findWhere @master_sources, {id: source.id }
        not master_source? or master_sources? and master_source.reference != source.reference

    recordChanges: (source)=>
        res = _.findWhere(@master_sources, {id: source.id })
        if res?
            res.reference = source.reference

    updateSource: (source, form)=>
        @scope.edit_form_submitted = true
        return unless form.$valid if form?
        if @hasChanged(source)
            @scope.loading[source.id] = true
            @Individual.updateSource(@getSourceParams(source), source, =>
                @scope.edit_form_submitted = false
                @scope.loading[source.id] = false
                @recordChanges(source)

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

    addSource: (source_text, form_add)=>
        @scope.form_add_submitted = true
        unless form_add?
            should_add = ['', undefined, null].indexOf(source_text) == -1 # not null values
            should_add = should_add and @getSourcesRefs().indexOf(source_text) is -1 # not existing values
            if should_add
                res = @__addSource(source_text)
            else
                res = false
            return res
        else
            # if no form is provided we return false
            return false unless form_add.$valid
            @scope.loading['global'] = true
            @__addSource(source_text, form_add)

    __addSource: (source_text, form_add)=>
        new_source =
            reference: source_text
            field: @field.name
        @Individual.createSource(@getIndividualParams(), new_source, (source)=>
                @scope.form_add_submitted = false
                @sources.push source
                @updateMasterSources()
                @scope.focus_new = false
                @scope.$broadcast @EVENTS.sources.added
                @scope.loading['global'] = false
            , =>
                @scope.form_add_submitted = false
                @scope.loading['global'] = false
        )

    getSources: => _.where @sources, field: @field.name

    getSourcesRefs: => _.map @getSources(), (s)-> s.reference

    updateMasterSources: =>
        @master_sources = angular.copy @sources

    hasSources: =>
        sources = @getSources()
        (not _.isEmpty sources) and _.some sources, (e)-> e? and e.reference?

    isSourceURLValid: (source)=>
        return false unless source?
        @UtilsFactory.isValidURL(source.reference)



angular.module('detective.controller').controller 'addSourcesModalCtrl', AddSourcesModalCtrl