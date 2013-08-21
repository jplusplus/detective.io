ContributeCtrl = ($scope, $routeParams, $rootScope, Individual, User)-> 
    
    # ──────────────────────────────────────────────────────────────────────────
    # Class methods
    # ──────────────────────────────────────────────────────────────────────────
    
    # A new individual for kick-star forms
    (initNewIndividual = ->
        $scope.new = 
            type       : ""
            loading    : false
            related_to : null
            fields     : new Individual name: ""
    # Self initiating function
    )()


    # ──────────────────────────────────────────────────────────────────────────
    # Scopes methods 
    # ──────────────────────────────────────────────────────────────────────────
    
    # Load an individual
    $scope.loadIndividual = (type, id)->
        index = -1
        # Looks for individual with this id
        _.each $scope.individuals, (i, idx)-> index = idx if i.fields.id is id
        # Stop here if we found an existing individual
        return index if index > -1 
        # Params to retreive the individual
        params = type: type, id: id
        # Future index of the new individual
        index  = $scope.individuals.length
        # Load the given individual
        $scope.individuals.push
            type       : type
            loading    : true
            related_to : null
            fields     : Individual.get params, =>                 
                # Disable loading state using the index set previously
                $scope.individuals[index].loading = false
        # Return the index of the new individual
        return index

    # Get resources list filtered by the current scope
    $scope.scopeResources = -> 
        resources = _.where $scope.resources, { scope: $scope.scope }
        # Add generic resources
        for r in ["organization", "person"]      
            if $scope.resources[r]? 
                resources.push( $scope.resources[r] )

        return resources

    # True if the given type is allowed
    $scope.isAllowedType = (type)->
        [
            "Relationship",
            "CharField",
            "DateTimeField",
            "URLField",
            "IntegerField"
        ].indexOf(type) > -1

    # When user submit a kick-start individual form
    $scope.addIndividual = (scroll=true)->
        unless $scope.new.fields.name is ""
            # Scroll to the individual
            $scope.scrollTo = $scope.individuals.length
            # Add the individual to the objects list
            $scope.individuals.push $scope.new 
            # Disable kickStart form
            $scope.showKickStart = false
            # Create a new individual object
            initNewIndividual()

    $scope.removeIndividual = (index=0)->
        $scope.individuals.splice(index, 1) if $scope.individuals[index]?

    
    # Returns true if the given field accept more related element
    $scope.isAllowedOneMore = (field)->       
        # Allow to create a new related individual if every current have an id 
        _.every field, (el)-> el.id?

    $scope.addRelated = (individual, key, type)->       
        individual.fields[key] = [] unless individual.fields[key]?
        individual.fields[key].push(name:"", type: type)

    $scope.removeRelated = (individual, key, index)->
        if individual.fields[key][index]?
            delete individual.fields[key][index]
            individual.fields[key].splice(index, 1) 
    
    # Edit the given related element
    $scope.editRelated = (individual, key, index, type)->
        related = individual.fields[key][index]        
        # Do the related exists ?
        if related? and related.id?
            # Load it (if needed)
            $scope.scrollTo = $scope.loadIndividual type.toLowerCase(), related.id

    
    $scope.askForNew = (el)->
        el? and el.name? and el.name isnt "" and not el.id?

    $scope.setNewIndividual = (el, type, parent, parentField)->        
        individual = new Individual el
        # Create the new entry obj
        $scope.new = 
            type       : type.toLowerCase()
            loading    : false
            related_to : parent
            fields     : individual
        # Create for the given parent field
        parent.fields[parentField] = [] unless parent.fields[parentField]?
        # Attachs the new element to its parent
        parent.fields[parentField].push individual
        # Add it to the list
        $scope.addIndividual()  
        # Then init the new form
        initNewIndividual()

    $scope.toggleReduce = (individual)->
        individual.reduce = not individual.reduce

    # Provides a way to preview the value of the given individual
    $scope.individualPreview = (i)->
        i.name or i.value or i.title or i.units or i.label or ""

    $scope.save = (individual)->        
        # Do not save a loading individual
        unless individual.loading
            # Loading mode on
            individual.loading = true
            params    = type: individual.type.toLowerCase()
            # Save the individual and
            # take care to specify the type
            individual.fields.$save(params, ->
                # Loading mode off
                individual.loading = false
                # Clean errors
                delete individual.error_message
            # Handles error
            , (response)->
                data = response.data
                # Loading mode off
                individual.loading = false
                # Add an error message
                individual.error_message = data.error_message if data.error_message?
                # Add the traceback
                individual.error_traceback = data.traceback if data.traceback?
            )

    # ──────────────────────────────────────────────────────────────────────────
    # Scope attributes
    # ──────────────────────────────────────────────────────────────────────────
    
    $scope.scope = $routeParams.scope
    # By default, hide the kick-start form
    $scope.showKickStart = false
    # Get the list of available resources
    $scope.resources = Individual.get()
    # Individual list
    $scope.individuals = []
    # Received an individual to edit
    if $routeParams.type? and $routeParams.id?
        # Load the inidividual
        $scope.scrollTo = $scope.loadIndividual $routeParams.type, $routeParams.id
    else
        # Index of the individual where to scroll 
        $scope.scrollTo  = -1



ContributeCtrl.$inject = ['$scope', '$routeParams', '$rootScope', 'Individual', 'User']
