class ContributeCtrl
    # Injects dependancies
    @$inject: ['$scope', '$routeParams', '$filter', 'Individual', 'IndividualForm']


    constructor: (@scope, @routeParams, @filter, @Individual, @IndividualForm)-> 
        # ──────────────────────────────────────────────────────────────────────
        # Methods and attributes available within the scope
        # ──────────────────────────────────────────────────────────────────────
        @scope.addIndividual     = @addIndividual
        @scope.addRelated        = @addRelated
        @scope.askForNew         = @askForNew
        @scope.editRelated       = @editRelated
        @scope.isAllowedOneMore  = @isAllowedOneMore
        @scope.isAllowedType     = @isAllowedType
        @scope.loadIndividual    = @loadIndividual
        @scope.relatedState      = @relatedState
        @scope.removeIndividual  = @removeIndividual
        @scope.removeRelated     = @removeRelated
        @scope.replaceIndividual = @replaceIndividual
        @scope.scopeResources    = @scopeResources
        @scope.scrollTo          = @scrollTo
        @scope.setNewIndividual  = @setNewIndividual
        @scope.showKickStart     = @showKickStart
        @scope.strToColor        = @filter("strToColor")

        # ──────────────────────────────────────────────────────────────────────
        # Scope watchers
        # ──────────────────────────────────────────────────────────────────────
        
        # When we update scrollIdx, reset its value after 
        # a short delay to allow scroll again
        @scope.$watch "scrollIdx", => 
            setTimeout =>
                @scope.scrollIdx = -1
                @scope.$apply()
            , 1200

        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        @scope.scope = @routeParams.scope        
        # By default, hide the kick-start form
        showKickStart = false        
        # Shortcut for child classes
        @scope.Individual = @Individual
        # Get the list of available resources
        @scope.resources = @Individual.get()
        # Prepare future individual
        @initNewIndividual()
        # Individual list
        @scope.individuals = @IndividualForm
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
        loading    : false
        master     : {}
        moreFields : []
        
        constructor: (scope, type="", fields={}, related_to=null)->
            @Individual = scope.Individual
            @meta       = scope.resources[type] or {}  
            @related_to = related_to
            @scope      = scope
            @type       = type            
            # Field param can be a number to load an individual
            @fields     = if isNaN(fields) then new @Individual(fields) else @load(fields)
            # Update meta when resources change
            @scope.$watch("resources", (value)=>
                @meta = value[@type] if value[@type]?
            , true)

        # Save the current individual form
        save: =>                  
            # Do not save a loading individual
            unless @loading
                # Loading mode on
                @loading = true
                params    = type: @type.toLowerCase()
                # Save the individual and
                # take care to specify the type
                @fields.$save(params, (master)=>
                    # Loading mode off
                    @loading = false
                    # Record master
                    @master = _.clone master
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
                @master  = _.clone master

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
 
        # Get the individual style
        individualStyle: ()=> "background-color": @scope.strToColor(@type)
    
        # Toggle the close attribute        
        close: => @isClosed = not @isClosed
        # Toggle the reduce attribute        
        reduce: => @isReduced = not @isReduced
        # Toggle the reduce attribute        
        invisibleFields: (meta)=> m for m in @meta unless @isVisible(m)
        showField: (field)=> @moreFields.push field       
        isSaved: => @fields.id? and angular.equals @master, @fields



    # ──────────────────────────────────────────────────────────────────────────
    # Class methods
    # ──────────────────────────────────────────────────────────────────────────
        
    # A new individual for kick-star forms
    initNewIndividual: (type, fields)=> @scope.new = new IndividualForm(@scope, type, fields)
        
    # Load an individual
    loadIndividual: (type, id, related_to=null)=>
        index = -1
        # Looks for individual with this id
        _.each @scope.individuals, (i, idx)=> index = idx if i.fields.id is id
        # Stop here if we found an existing individual
        return index if index > -1 
        # Create the new form        
        form = new IndividualForm(@scope, type, id, related_to)
        # Create an individual        
        @scope.individuals.push form        
        # Return the index of the new individual
        return index

    # Get resources list filtered by the current scope
    scopeResources: => 
        resources = _.where @scope.resources, { scope: @scope.scope }
        # Add generic resources
        for r in ["organization", "person"]      
            if @scope.resources[r]? 
                resources.push( @scope.resources[r] )

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
    addIndividual: (scroll=true)=>
        unless @scope.new.fields.name is ""   
            # Disable kickStart form
            @scope.showKickStart = false
            # Create the form
            form = @initNewIndividual(@scope.new.type, @scope.new.fields)
            # Is that field a searchable field ?
            if @scope.new.fields.name
                params = type: @scope.new.type, name: @scope.new.fields.name
                # Look for individual with the same name
                form.similars = @Individual.query params
            # Reset the new field
            @scope.new = new IndividualForm(@scope)
            # Scroll to the individual
            @scope.scrollIdx = @scope.individuals.length if scroll
            # Add the individual to the objects list
            @scope.individuals.push form

    removeIndividual: (index=0)=>
        @scope.individuals.splice(index, 1) if @scope.individuals[index]?            

    replaceIndividual: (index=0, id)=>
        individual = @scope.individuals[index]
        individual.loading  = true        
        individual.similars = [] 
        individual.fields   = @Individual.get {type: individual.type, id: id}, (master)->                 
            # Disable loading state
            individual.loading = false
            # Record the database version of the individual
            individual.master  = _.clone master
    
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
        # Do the related exists ?
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

    setNewIndividual: (master, type, parent, parentField, index=-1)=>        
        individual = new @Individual master
        # Ensure that the type isn't title-formated
        type       = type.toLowerCase()
        # Create the new entry obj
        @initNewIndividual(type, individual, parent)           
        # Create for the given parent field
        parent.fields[parentField] = [] unless parent.fields[parentField]?
        
        if index == -1
            # Attachs the new element to its parent            
            parent.fields[parentField].push individual
        else
            delete @master
            # Update the new element with an Individual class            
            parent.fields[parentField][index] = individual

        # Add it to the list using @scope.new
        @scope.addIndividual()  

    # Change the scrollIdx to scroll to the given individual
    scrollTo: (individual)=>
        index = -1
        # Looks for individual that match with the given one
        _.each @scope.individuals, (i, idx)=> index = idx if i == individual
        # Update the scrollIdx
        @scope.scrollIdx = index    

angular.module('detective').controller 'contributeCtrl', ContributeCtrl