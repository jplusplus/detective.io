ContributeCtrl = ($scope, $routeParams, $rootScope, Individual, User)-> 
    
    $scope.scope = $routeParams.scope
    # By default, hide the kick-start form
    $scope.showKickStart = false
    # Individual list
    $scope.individuals = [        
        type       : "price"
        loading    : false
        related_to : null
        fields     : Individual.get(type:"price", id:15)
    ]
    # Get the list of available resources
    $scope.resources = Individual.get()

    # A new individual for kick-star forms
    (initNewIndividual = ->
        $scope.new = 
            type       : ""
            loading    : false
            related_to : null
            fields     : new Individual name: ""
    # Self initiating function
    )()

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
            # Add the individual to the objects list
            $scope.individuals.push $scope.new 
            # Disable kickStart form
            $scope.showKickStart = false
            # Create a new individual object
            initNewIndividual()

    $scope.removeIndividual = (index=0)->
        $scope.individuals.splice(index, 1) if $scope.individuals[index]?

    $scope.addOne = (individual, key, type)->       
        individual.fields[key] = [] unless individual.fields[key]?
        individual.fields[key].push(name:"", type: type)
    
    # Returns true if the given field accept more related element
    $scope.isAllowedOneMore = (field)->       
        # Allow to create a new related individual if every current have an id 
        _.every field, (el)-> el.id?

    $scope.removeOne = (individual, key, index)->
        if individual.fields[key][index]?
            delete individual.fields[key][index]
            individual.fields[key].splice(index, 1) 
    
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


ContributeCtrl.$inject = ['$scope', '$routeParams', '$rootScope', 'Individual', 'User']
