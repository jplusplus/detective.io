ContributeCtrl = ($scope, $routeParams, $rootScope, Individual, User)-> 
    
    $scope.scope = $routeParams.scope
    # By default, hide the kick-start form
    $scope.showKickStart = false
    # Individual list
    $scope.individuals = []
    # Get the list of available resources
    $scope.resources = Individual.get()

    # A new individual for kick-star forms
    (initNewIndividual = ->
        $scope.new = 
            type    : ""
            loading : false
            fields  : new Individual name: ""
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
            # Clones the object to avoid inserting duplicates
            o = $.extend(true, {}, $scope.new)
            # Add the clone to the objects list
            $scope.individuals.push(o)
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

    $scope.setNewIndividual = (el, type)->
        # Create the new entry obj
        $scope.new = 
            type    : type.toLowerCase()
            loading : false
            fields  : new Individual name: el.name        
        # Remove name
        el.name = ""
        # Add it to the list
        $scope.addIndividual()        
        # Then init the new form
        initNewIndividual()


    $scope.toggleReduce = (individual)->
        individual.reduce = not individual.reduce

    $scope.save = (individual)->        
        # Do not save a loading individual
        unless individual.loading
            # Loading mode on
            individual.loading = true
            # Save the individual and
            # take care to specify the type
            individual.fields.$save type: individual.type.toLowerCase(), ->
                # Loading mode off
                individual.loading = false

ContributeCtrl.$inject = ['$scope', '$routeParams', '$rootScope', 'Individual', 'User']
