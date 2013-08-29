class ContributeCtrl
    # Injects dependancies
    @$inject: ['$scope', '$routeParams', '$filter', 'Individual']

    constructor: (@scope, @routeParams, @filter, @Individual)-> 
        # ──────────────────────────────────────────────────────────────────────
        # Methods and attributes available within the scope
        # ──────────────────────────────────────────────────────────────────────
        @scope.addIndividual     = @addIndividual
        @scope.addRelated        = @addRelated
        @scope.askForNew         = @askForNew
        @scope.editRelated       = @editRelated
        @scope.individualStyle   = @individualStyle
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
        # Get the list of available resources
        @scope.resources = @Individual.get()
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
    # Class methods
    # ──────────────────────────────────────────────────────────────────────────
        
    # A new individual for kick-star forms
    initNewIndividual: (set=true)=>
        individual = 
            type       : ""
            loading    : false
            related_to : null
            fields     : new @Individual name: ""
            master     : {}
            save       : @save
            close      : -> @isClosed = not @isClosed
            reduce     : -> @isReduced = not @isReduced
            isSaved    : -> @fields.id? and angular.equals @master, @fields
        # Set the new individual
        if set then @scope.new = individual else individual        

    
    # Load an individual
    loadIndividual: (type, id, related_to=null)=>
        index = -1
        # Looks for individual with this id
        _.each @scope.individuals, (i, idx)=> index = idx if i.fields.id is id
        # Stop here if we found an existing individual
        return index if index > -1 
        # Params to retreive the individual
        params = type: type, id: id
        # Future index of the new individual
        index  = @scope.individuals.length
        # Create an individual
        @scope.individuals.push @initNewIndividual(false)        
        @scope.individuals[index].type       = type
        @scope.individuals[index].loading    = true
        @scope.individuals[index].related_to = related_to
        # Load the given individual        
        @scope.individuals[index].fields = @Individual.get params, (master)=>  
            # Disable loading state
            @scope.individuals[index].loading = false
            # Record the database version of the individual
            @scope.individuals[index].master  = _.clone master

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

    # Get the individual style
    individualStyle: (individual)=>
        "background-color": @scope.strToColor(individual.type)

    # When user submit a kick-start individual form
    addIndividual: (scroll=true)=>
        unless @scope.new.fields.name is ""   
            # Is that field a searchable field ?
            if @scope.new.fields.name
                params = type: @scope.new.type, name: @scope.new.fields.name
                # Look for individual with the same name
                @scope.new.similars = @Individual.query params
            # Scroll to the individual
            @scope.scrollIdx = @scope.individuals.length if scroll
            # Add the individual to the objects list
            @scope.individuals.push @scope.new 
            # Disable kickStart form
            @scope.showKickStart = false
            # Create a new individual object
            @initNewIndividual()

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
            @scope.scrollIdx = @scope.loadIndividual type.toLowerCase(), related.id, individual

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
        @initNewIndividual()   
        # Complete the new obj     
        @scope.new.type       = type
        @scope.new.related_to = parent
        @scope.new.fields     = individual

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
    
    save: ()->        
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

angular.module('detective').controller 'contributeCtrl', ContributeCtrl