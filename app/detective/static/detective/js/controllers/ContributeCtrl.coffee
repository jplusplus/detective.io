class window.ContributeCtrl
    # Injects dependencies
    @$inject: ['$scope', '$modal', '$state', '$stateParams', '$filter', '$timeout', '$location', 'Individual', 'Summary', 'Page', 'User', 'topic', 'forms', 'UtilsFactory']

    constructor: (@scope, @modal, @state, @stateParams, @filter, @timeout, @location, @Individual, @Summary, @Page, @User, topic, @forms, @UtilsFactory)->
        @Page.title "Contribute"
        # Global loading mode
        Page.loading false
        # ──────────────────────────────────────────────────────────────────────
        # Methods and attributes available within the scope
        # ──────────────────────────────────────────────────────────────────────
        @scope.addIndividual       = @addIndividual
        @scope.addInfo             = @addInfo
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
        @scope.seeDetails          = @seeDetails
        @scope.scrollTo            = @scrollTo
        @scope.setNewIndividual    = @setNewIndividual
        @scope.showKickStart       = @showKickStart
        @scope.isVisibleAdditional = @isVisibleAdditional
        @scope.strToColor          = @filter("strToColor")
        @scope.isRich              = @isRich
        @scope.focusField          = @focusField
        @scope.unfocusField        = @unfocusField
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        @scope.topic    = @stateParams.topic
        @scope.username = @stateParams.username
        @scope.type     = @stateParams.type
        @scope.id       = @stateParams.id
        @scope.meta     = topic
        # check if user is allowed to contribute
        @scope.isOverfillingThePlan = topic.author.profile.nodes_max > -1 and topic.author.profile.nodes_count[@stateParams.topic] >= topic.author.profile.nodes_max
        # Get the list of available resources
        @scope.forms    = @forms
        # By default, hide the kick-start form
        showKickStart   = false
        # Shortcuts for child classes
        @scope.Individual   = @Individual
        @scope.stateParams  = @stateParams
        @scope.UtilsFactory = @UtilsFactory
        @scope.modal        = @modal
        # Prepare future individual
        @initNewIndividual()
        # Individual list
        @scope.individuals = []
        # Received an individual to edit
        if @location.search().type? and @location.search().id?
            # Load the inidividual
            @scope.scrollIdx = @scope.loadIndividual @scope.type, @scope.id
        else
            # Index of the individual where to scroll
            @scope.scrollIdx  = -1

        # ──────────────────────────────────────────────────────────────────────
        # Scope watchers
        # ──────────────────────────────────────────────────────────────────────

        # When we update scrollIdx, reset its value after
        # a short delay to allow scroll again
        @scope.$watch "scrollIdx", (v)=>
            @timeout (=> @scope.scrollIdx = -1), 1200


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
            # List of field sources that are updating
            @updating_sources = {}
            # Avoid object references
            fields      = angular.copy fields
            # Copy of the database's fields
            @master     = angular.copy fields
            # List of additional visible fields
            @moreFields = []
            @similars   = []
            # Is that model a searchable individual ?
            # Load similar individual to avoid duplicates
            # AFTER the individual is created.
            scope.$on("individual:created", @getSimilars) if fields.name?
            # We may have to refresh this individual
            scope.$on("individual:created", @shouldRefresh)
            # Class attributes from parameters
            # ──────────────────────────────────────────────────────────────────
            @Individual   = scope.Individual
            @UtilsFactory = scope.UtilsFactory
            @modal        = scope.modal
            @meta         = scope.forms[type] or {}
            @related_to   = related_to
            @scope        = scope
            @type         = type.toLowerCase()
            # All source fields
            @sources = {}
            @isNew   = not fields.id?
            # Field param can be a number to load an individual
            @fields  = if isNaN(fields) then new @Individual(fields) else @load(fields)
            # Class watchers
            # ──────────────────────────────────────────────────────────────────
            # The data changed
            @scope.$watch (=>@fields), @onChange, true

            do @unfocusField

        onChange: (current)=>
            # Individual not created yet
            return unless current.id?
            # Propagation of the new individual
            if @isNew
                # Brodcast and object
                @scope.$broadcast "individual:created",
                    individual: current
                    related_to: @related_to ? null
                # It's not a new individual now
                @isNew = no
            # Looks for duplicated entities in fields. Mark them as duplicated. Prevents duplicated relationships (#521)
            for name, value of @fields
                if value? and typeof(value) is "object" and name isnt "field_sources" and name.indexOf("$") != 0
                    exist = {}
                    for entity in value
                        entity.$duplicated = exist[entity.id]? and exist[entity.id]
                        exist[entity.id] = true
            # Only if master is completed
            unless _.isEmpty(@master) or @loading
                changes = @getChanges()
                # Looks for the differences and update the db if needed
                @update(changes) if not _.isEmpty(changes) and not @data_are_updating

        getSimilars: (event, args)=>
            # Only load similar individual if the new one is the current instance
            return unless args.individual.id is @fields.id
            params =
                type:  @type
                id:    "search"
                q:     @fields.name
            # Look for individual with the same name
            @Individual.query params, (d)=>
                # Remove the one we just created
                d = _.filter d, (e)=> e.id isnt @fields.id
                # Similar entries
                @similars = d

        shouldRefresh: (event, args)=>
            # Refresh only related individual
            if args.related_to? and args.individual.id is @fields.id
                # Get relationships field
                relationships = _.where @meta.fields, type: "Relationship"
                relationships = _.pluck relationships, "name"
                # Does this individual have relationships fields?
                if relationships.length
                    # Set loading state to the relationships fields
                    @updating[rel] = yes for rel in relationships
                    # Load the individual
                    @Individual.get type: @type, id: @fields.id, (individual)=>
                        # Reload the relationships fields
                        for rel in relationships
                            if individual[rel]?
                                # Update the master too in order
                                # to avoid new reloading
                                angular.extend @master[rel], individual[rel]
                                angular.extend @fields[rel], individual[rel]
                            # Field no more loading
                            delete @updating[rel]

        getChanges: (prev=@master, now=@fields)=>
            changes = {}
            # Function to remove nested resources without id
            clean   = (val, name="")->
                # copy the current value
                val = angular.copy val
                value_to_return = val
                if val instanceof Date
                    # remove timezone offset
                    val.setHours(val.getHours() - val.getTimezoneOffset() / 60)
                    # Convert date object to string
                    value_to_return = val.toJSON()
                else if typeof(val) is "object" and name isnt "field_sources"
                    # Fetch each nested value
                    value_to_return = []
                    for pc of val
                        # ignore the nested values without id
                        continue unless val[pc].id?
                        # ignore duplicated. Prevents duplicated relationships (#521)
                        if not _.findWhere(value_to_return, {id: val[pc].id})?
                            # Create a new object that only contains an id
                            value_to_return.push(id: val[pc].id)
                else if typeof(val) is "boolean"
                    value_to_return = val or false
                else if value_to_return == "" or value_to_return == undefined or _.isEmpty(value_to_return)
                    # Empty input must be null
                    value_to_return = null
                return value_to_return

            for prop of now
                val = clean(now[prop], prop)
                # Remove resource methods
                # and angular properties (that start with $)
                if typeof(val) isnt "function" and prop.indexOf("$") != 0
                    # Previous and new value are different
                    unless angular.equals clean(prev[prop], prop), val
                        changes[prop] = val
            return changes

        # Generates the permalink to this individual
        permalink: =>
            return false unless @fields.id? and @scope.topic
            return "/#{@scope.username}/#{@scope.topic}/#{@type}/#{@fields.id}"

        hasSrefOptions: =>
            @fields.id? and @scope.topic?

        srefOptions: =>
            return false unless @fields.id and @scope.topic
            return {
                username: @scope.username
                topic   : @scope.topic
                type    : @type
                id      : @fields.id
            }


        # Event when fields changed
        update: (data)=>
            @data_are_updating = true
            params = type: @type, id: @fields.id
            # Notice that the field is loading
            @updating = _.extend @updating, data
            # Patch the current individual
            @Individual.update params, data, (res)=>
                # Record master
                @master = _.extend @master, res
                @data_are_updating = false
                # Notices that we stop to load the field
                @updating = _.omit(@updating, _.keys(data))
                # Prevent communications between forms
                @updating = angular.copy @updating
                # Propagation
                @scope.$broadcast "individual:updated", @fields
            , (error)=>
                if error.status == 404
                    @isClosed   = true
                    @isRemoved  = true

        # Save the current individual form
        save: =>
            # Do not save a loading individual
            unless @loading
                # Loading mode on
                @loading = true
                params   = type: @type
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
            params = type: @type, id: id
            # Load the given individual
            @fields = @Individual.get params, (master)=>
                    # Disable loading state
                    @loading = false
                    # Record the database version of the individual
                    @master  = angular.copy master
                    @sources = _.object _.map(@fields.field_sources, (fs)-> [fs.field, fs.url])
                    # Propagation
                    @scope.$broadcast "individual:loaded", @fields
                , (error)=>
                    @loading = false
                    # handle 404 response for entity loading
                    if error.status == 404
                        @isClosed  = true
                        @isRemoved = false
                        @isNotFound = true

        getSources: (field)=> _.where @fields.field_sources, field: field.name

        hasSources: (field)=>
            sources = @getSources(field)
            (not _.isEmpty sources) and _.some sources, (e)-> e? and e.reference?

        openSourcesModal: (field)=>
            fields = @modal.open
                templateUrl: '/partial/topic.contribute.add-sources.html'
                controller : 'addSourcesModalCtrl'
                resolve    :
                    # Load the properties of this field
                    fields: => @fields
                    # Invididual type
                    meta: =>
                        updating: @updating_sources
                        type: @type
                        id: @fields.id
                    field: => field

            fields.result.then (res)=>
                @updating_sources[field.name] = no
                console.log 'sources updated'
                @fields.field_sources = res.field_sources

        # True if the given field can be edit
        isEditable: (field)=>
            return not field.rules.is_editable? or field.rules.is_editable is yes

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

        delete: (index, msg='Are you sure you want to delete this node?')=>
            # Ask user for confirmation
            if confirm(msg)
                @Individual.delete
                    id   : @fields.id
                    type : @type
                @scope.removeIndividual(index)

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

        unfocusField: =>
            @focusedField =
                field : undefined
                source : no

        isFieldFocused: (field) =>
            field? and field.name? and @focusedField.field is field.name

        isSourceFormOpened: (field) =>
            (@isFieldFocused field) and @focusedField.source

        toggleSourceForm: (field) =>
            if @isFieldFocused field
                @focusedField.source = !@focusedField.source



    # ──────────────────────────────────────────────────────────────────────────
    # Class methods
    # ──────────────────────────────────────────────────────────────────────────

    focusField: (individual, field) =>
        for loop_individual in @scope.individuals
            if individual is loop_individual
                if loop_individual.focusedField.field isnt field.name
                    loop_individual.focusedField.field = field.name
                    loop_individual.focusedField.source = no
            else
                do loop_individual.unfocusField

    unfocusField: =>
        for loop_individual in @scope.individuals
            do loop_individual.unfocusField

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
        # Only show resources with a name
        resources = _.filter @forms, (r)->
            r.rules? and r.rules.is_searchable and r.rules.is_editable
        return resources

    # True if the given type is allowed
    isAllowedType: (type)=>
        [
            "Relationship",
            "RelationshipProperties",
            "CharField",
            "DateTimeField",
            "URLField",
            "IntegerField",
            "BooleanField"
        ].indexOf(type) > -1


    # When user submit a kick-start individual form
    addIndividual: (scroll=true, form=null)=>
        unless @scope.new.fields.name is ""
            # Disable kickStart form
            @scope.showKickStart = false
            # Create the form
            form = @initNewIndividual(@scope.new.type, @scope.new.fields) if form is null
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
        # Parameters of the individual to delete
        toDelete =
            type : individual.type
            id   : individual.fields.id
        # Remove the node we're about to replace
        # (no feedback)
        @Individual.delete(toDelete)
        # Build parameters to load the individual from database
        params =
            type : individual.type
            id   : id
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

    addInfo: (individual, field, target)=>
        # Do not open the modal twice
        return if @relationshipProperties?

        params =
            type  : individual.type
            id    : individual.fields.id
            field : field
            target: target.id

        # Model that describes the relationship
        through = _.findWhere(individual.meta.fields, name: field).rules.through


        @relationshipProperties = @modal.open
            templateUrl: '/partial/topic.contribute.relationship-properties.html'
            controller : 'relationshipPropertiesCtrl as form'
            resolve    :
                # Load the properties of this field
                properties  : => @Individual.relationships(params).$promise
                # Field of the model
                meta        : => @forms[do through.toLowerCase]
                # An object describing the relationship
                relationship: =>
                    # The model that describes this relationship
                    through: through
                    # Here source and target order are completely arbitrary
                    source: individual.fields
                    target: target

        # Disabling function
        disable = => delete @relationshipProperties
        # Remove the instance when closing the modal
        @relationshipProperties.result.then disable, disable

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
        ###
        Return the visual state of the field.
        - `input`  for editable fields,
        - `linked` for field which represent an Individal but isn't duplicated. The field will be shown as an uneditable field.
        ###
        switch true
            when related instanceof @Individual or (related.id? and not related.$duplicated) then 'linked'
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

    seeDetails: (individual)=>
        @state.go 'user-topic-detail', individual.srefOptions()

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

    isRich: (field) =>
        field.rules.is_rich or no


angular.module('detective.controller').controller 'contributeCtrl', ContributeCtrl
