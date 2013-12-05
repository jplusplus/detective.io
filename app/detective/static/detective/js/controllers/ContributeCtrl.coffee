class ContributeCtrl
    # Injects dependancies
    @$inject: ['$scope', '$routeParams', '$filter', 'Individual', 'Summary', 'IndividualForm', 'Page']


    constructor: (@scope, @routeParams, @filter, @Individual,  @Summary, @IndividualForm, @Page)->
        @Page.title "Contribute"
        # Global loading mode
        Page.loading true
        # ──────────────────────────────────────────────────────────────────────
        # Methods and attributes available within the scope
        # ──────────────────────────────────────────────────────────────────────
        @scope.addIndividual       = @addIndividual
        @scope.addRelated          = @addRelated
        @scope.askForNew           = @askForNew
        @scope.editRelated         = @editRelated
        @scope.isAllowedOneMore    = @isAllowedOneMore
        @scope.isAllowedType       = @isAllowedType
        @scope.loadIndividual      = @loadIndividual
        @scope.relatedState        = @relatedState
        @scope.removeIndividual    = @removeIndividual
        @scope.removeRelated       = @removeRelated
        @scope.replaceIndividual   = @replaceIndividual
        @scope.topicResources      = @topicResources
        @scope.scrollTo            = @scrollTo
        @scope.setNewIndividual    = @setNewIndividual
        @scope.showKickStart       = @showKickStart
        @scope.isVisibleAdditional = @isVisibleAdditional
        @scope.strToColor          = @filter("strToColor")
        @scope.modelTopic          = (m)=> if @scope.resources? then @scope.resources[m.toLowerCase()].topic

        # ──────────────────────────────────────────────────────────────────────
        # Scope watchers
        # ──────────────────────────────────────────────────────────────────────

        # When we update scrollIdx, reset its value after
        # a short delay to allow scroll again
        @scope.$watch "scrollIdx", (v)=>
            setTimeout =>
                @scope.scrollIdx = -1
                @scope.$apply()
            , 1200

        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        @scope.topic = @routeParams.topic
        # By default, hide the kick-start form
        showKickStart = false
        # Shortcuts for child classes
        @scope.Individual  = @Individual
        @scope.routeParams = @routeParams
        # Get the list of available resources
        @scope.resources = @Summary.get {id: "forms", topic: @scope.topic }, => @Page.loading(false)
        # Prepare future individual
        @initNewIndividual()
        # Individual list
        @scope.individuals = []
        # Received an individual to edit
        if @routeParams.type? and @routeParams.id?
            # Load the inidividual
            @scope.scrollIdx = @scope.loadIndividual @routeParams.type, @routeParams.id
        else
            # Index of the individual where to scroll
            @scope.scrollIdx  = -1


    # ──────────────────────────────────────────────────────────────────────────
    # IndividualForm embeded class
    # ──────────────────────────────────────────────────────────────────────────
    class IndividualForm

        constructor: (scope, type="", fields={}, related_to=null)->
            # Class default attributes
            # ──────────────────────────────────────────────────────────────────
            # True if the individual is loading
            @loading    = false
            # List of field that are updating
            @updating   = {}
            # Copy of the database's fields
            @master     = angular.copy fields,
            # List of additional visible fields
            @moreFields = []
            # Class attributes from parameters
            # ──────────────────────────────────────────────────────────────────
            @Individual = scope.Individual
            @meta       = scope.resources[type] or {}
            @related_to = related_to
            @scope      = scope
            @type       = type.toLowerCase()
            # Field param can be a number to load an individual
            @fields     = if isNaN(fields) then new @Individual(fields) else @load(fields)
            # Class watchers
            # ──────────────────────────────────────────────────────────────────
            # Update meta when resources change
            @scope.$watch "resources", (value)=>
                @meta = value[@type] if value[@type]?
            , true
            # The data changed
            @scope.$watch (=>@fields), @onChange, true

        onChange: ()=>
            # Individual not created yet
            return unless @fields.id?
            # Only if master is completed
            unless _.isEmpty(@master) or @loading
                changes = @getChanges()
                # Looks for the differences and update the db if needed
                @update(changes) unless _.isEmpty(changes)

        getChanges: (prev=@master, now=@fields)=>
            changes = {}
            # Function to remove nested resources without id
            clean   = (val)->
                # copy the current value
                val = angular.copy val
                if val instanceof Date
                    # Convert date object to string
                    val = val.toJSON()
                else if typeof(val) is "object"
                    # Fetch each nested value
                    for pc of val
                        # Remove the nested values without id
                        unless val[pc].id?
                            delete val[pc]
                            # Apply splice only on array
                            val.splice(pc) if val instanceof Array
                            # Go to the next value
                            continue
                        # Create a new object that only contains an id
                        val[pc] = id: val[pc].id

                else if val == "" or val == undefined
                    # Empty input must be null
                    val = null
                val
            for prop of now
                val = clean(now[prop])
                # Remove resource methods
                # and angular properties (that start with $)
                if typeof(val) isnt "function" and prop.indexOf("$") != 0
                    # Previous and new value are different
                    unless angular.equals clean(prev[prop]), val
                        changes[prop] = val
            changes

        # Generates the permalink to this individual
        permalink: =>
            return false unless @fields.id? and @meta.topic
            return "/#{@meta.topic}/#{@type}/#{@fields.id}"

        # Event when fields changed
        update: (data)=>
            params = type: @type, topic: @getTopic(), id: @fields.id
            # Notice that the field is loading
            @updating = _.extend @updating, data
            # Patch the current individual
            @Individual.update params, data, (res)=>
                # Record master
                @master = _.extend @master, res
                # Notices that we stop to load the field
                @updating = _.omit(@updating, _.keys(data))
                # Prevent communications between forms
                @updating = angular.copy @updating
            , (error)=>
                if error.status == 404
                    @isClosed   = true
                    @isRemoved  = true

        # Returns individual's topic
        getTopic: => @meta.topic or @scope.routeParams.topic

        # Save the current individual form
        save: =>
            # Do not save a loading individual
            unless @loading
                # Loading mode on
                @loading = true
                params   = type: @type, topic: @getTopic()
                # Save the individual and
                # take care to specify the type
                @fields.$save(params, (master)=>
                    # Loading mode off
                    @loading = false
                    # Record master
                    @master = angular.copy master
                    # Clean errors
                    delete @error_message
                # Handles error
                , (response)=>
                    data = response.data
                    # Loading mode off
                    @loading = false
                    # Add an error message
                    @error_message = data.error_message if data.error_message?
                    # Add the traceback
                    @error_traceback = data.traceback if data.traceback?
                )

        # Load an individual using its id
        load: (id, related_to=null)=>
            @loading    = true
            @related_to = related_to
            # Params to retreive the individual
            params = type: @type, id: id, topic: @getTopic()
            # Load the given individual
            @fields = @Individual.get params, (master)=>
                    # Disable loading state
                    @loading = false
                    # Record the database version of the individual
                    @master  = angular.copy master
                , (error)=>
                    @loading = false
                    # handle 404 response for entity loading
                    if error.status == 404
                        @isClosed  = true
                        @isRemoved = false
                        @isNotFound = true


        # True if the given field is visible
        isVisible: (field)=>
            return false unless field? and field.rules?
            value = @fields[field.name]
            # This field is always visible
            field.rules.is_visible or
            # Or the user ask to see it
            @moreFields.indexOf(field) > -1 or
            # Or the value of this field ins't empty
            (value? and value != null and value.length)

        # Toggle the close attribute
        close: => @isClosed = not @isClosed
        # Get invisible field with this individual
        invisibleFields: (meta)=>
            fields = []
            if @meta.fields?
                for f in @meta.fields
                    fields.push(f) if @scope.isVisibleAdditional(@)(f)
            fields
        showField: (field)=> @moreFields.push field
        isSaved: => @fields.id? and _.isEmpty( @getChanges() )



    # ──────────────────────────────────────────────────────────────────────────
    # Class methods
    # ──────────────────────────────────────────────────────────────────────────

    # A new individual for kick-star forms
    initNewIndividual: (type, fields, related_to)=>
        @scope.new = new IndividualForm(@scope, type, fields, related_to)

    # Load an individual
    loadIndividual: (type, id, related_to=null)=>
        index = -1
        # Looks for individual with this id
        _.each @scope.individuals, (i, idx)=>
            index = idx if parseInt(i.fields.id) is parseInt(id)
        # Stop here if we found an existing individual
        if index > -1
            @scope.individuals[index].isClosed = false
            return index
        # Create the new form
        form = new IndividualForm(@scope, type, id, related_to)
        # Create an individual
        index = @scope.individuals.push(form) - 1
        # Return the index of the new individual
        return index

    # Get resources list filtered by the current topic
    topicResources: =>
        return [] unless @scope.resources.$resolved
        # Only show resources with a name
        resources = _.filter @scope.resources, (r)->
            r.rules? and r.rules.is_searchable and r.rules.is_editable
        return resources

    # True if the given type is allowed
    isAllowedType: (type)=>
        [
            "Relationship",
            "CharField",
            "DateTimeField",
            "URLField",
            "IntegerField"
        ].indexOf(type) > -1


    # When user submit a kick-start individual form
    addIndividual: (scroll=true, form=null)=>
        unless @scope.new.fields.name is ""
            # Disable kickStart form
            @scope.showKickStart = false
            # Create the form
            form = @initNewIndividual(@scope.new.type, @scope.new.fields) if form is null
            # Is that field a searchable field ?
            if @scope.new.fields.name
                params =
                    type:  @scope.new.type
                    id:    "search"
                    q:     @scope.new.fields.name
                    topic: @scope.new.meta.topic
                # Look for individual with the same name
                @Individual.query params, (d)=>
                    # Remove the one we just created
                    d = _.filter d, (e)=> e.id isnt form.fields.id
                    # Similar entries
                    form.similars = d
            # Reset the new field
            @scope.new = new IndividualForm(@scope)
            # Scroll to the individual
            @scope.scrollIdx = @scope.individuals.length if scroll
            # Add the individual to the objects list
            @scope.individuals.push form
            # Return the new form
            form

    removeIndividual: (index=0)=>
        @scope.individuals.splice(index, 1) if @scope.individuals[index]?

    replaceIndividual: (index=0, id)=>
        individual = @scope.individuals[index]
        individual.loading  = true
        individual.similars = []
        topic = @scope.resources[individual.type].topic
        # Parameters of the individual to delete
        toDelete =
            type : individual.type
            id   : individual.fields.id
            topic: topic
        # Remove the node we're about to replace
        # (no feedback)
        @Individual.delete(toDelete)
        # Build parameters to load the individual from database
        params =
            type : individual.type
            id   : id
            topic: topic
        # Then load the individual
        individual.fields = @Individual.get params, (master)->
            # Disable loading state
            individual.loading = false
            # Record the database version of the individual
            individual.master  = angular.copy master

    # Returns true if the given field accept more related element
    isAllowedOneMore: (field)=>
        # Allow to create a new related individual if every current have an id
        _.every field, (el)=> el.id?

    addRelated: (individual, key, type)=>
        individual.fields[key] = [] unless individual.fields[key]?
        individual.fields[key].push(name:"", type: type)

    removeRelated: (individual, key, index)=>
        if individual.fields[key][index]?
            delete individual.fields[key][index]
            individual.fields[key].splice(index, 1)

    # Edit the given related element
    editRelated: (individual, key, index, type)=>
        related = individual.fields[key][index]
        # Does the related exist ?
        if related? and related.id?
            # Load it (if needed)
            @scope.scrollIdx = @scope.loadIndividual type.toLowerCase(), related.id,  individual

    relatedState: (related)=>
        switch true
            when related instanceof @Individual or related.id? then 'linked'
            else 'input'

    askForNew: (related)=>
        related? and not related instanceof @Individual or
        (related.name? and related.name isnt "" and not related.id?)

    setNewIndividual: (fields, type, parent, parentField, index=-1)=>
        # Avoid object sharing
        fields = angular.copy(fields)
        # Ensure that the type isn't title-formatted
        type = type.toLowerCase()
        # Create the new entry obj
        form = new IndividualForm(@scope, type, fields, parent)
        # Create for the given parent field
        parent.fields[parentField] = [] unless parent.fields[parentField]?
        # Individual not found
        if index == -1
            # Attachs the new element to its parent
            parent.fields[parentField].push form.fields
        else
            # Update the new element with an Individual class
            parent.fields[parentField][index] = form.fields
        # Add it to the list using @scope.new
        # and save the form a first time
        @scope.addIndividual(true, form).save()

    # Change the scrollIdx to scroll to the given individual
    scrollTo: (individual)=>
        index = -1
        # Looks for individual that match with the given one
        _.each @scope.individuals, (i, idx)=> index = idx if i == individual
        # Update the scrollIdx
        @scope.scrollIdx = index

    # Closure filter
    isVisibleAdditional: (individual)=>
        # True if the given field must be show into the inidividual
        (field)=>
            not individual.isVisible(field) and @isAllowedType(field.type)

angular.module('detective').controller 'contributeCtrl', ContributeCtrl
