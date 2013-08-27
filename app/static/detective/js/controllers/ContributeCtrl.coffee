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
    $scope.loadIndividual = (type, id, related_to=null)->
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
            closed     : false
            related_to : related_to
            similars   : []            
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

    # Get the individual style
    $scope.individualStyle = (individual)->
        "background-color": strToColor(individual.type)

    # When user submit a kick-start individual form
    $scope.addIndividual = (scroll=true)->
        unless $scope.new.fields.name is ""   
            # Is that field a searchable field ?
            if $scope.new.fields.name
                params = type: $scope.new.type, name: $scope.new.fields.name
                # Look for individual with the same name
                $scope.new.similars = Individual.query params
            # Scroll to the individual
            $scope.scrollIdx = $scope.individuals.length if scroll
            # Add the individual to the objects list
            $scope.individuals.push $scope.new 
            # Disable kickStart form
            $scope.showKickStart = false
            # Create a new individual object
            initNewIndividual()

    $scope.toggleIndividual = (index=0)->
        if $scope.individuals[index]?
            $scope.individuals[index].closed = not $scope.individuals[index].closed

    $scope.removeIndividual = (index=0)->
        $scope.individuals.splice(index, 1) if $scope.individuals[index]?            

    $scope.replaceIndividual = (index=0, id)->
        individual = $scope.individuals[index]
        individual.loading  = true        
        individual.similars = [] 
        individual.fields   = Individual.get {type: individual.type, id: id}, =>                 
            # Disable loading state using the index set previously
            $scope.individuals[index].loading = false        
    
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
            $scope.scrollIdx = $scope.loadIndividual type.toLowerCase(), related.id, individual

    $scope.relatedState = (related)->
        switch true
            when related instanceof Individual or related.id? then 'linked'
            else 'input'
    
    $scope.askForNew = (related)->            
        related? and not related instanceof Individual or
        (related.name? and related.name isnt "" and not related.id?)

    $scope.setNewIndividual = (master, type, parent, parentField, index=-1)->        
        individual = new Individual master
        # Ensure that the type isn't title-formated
        type       = type.toLowerCase()
        # Create the new entry obj
        $scope.new = 
            type       : type
            loading    : false
            closed     : false
            related_to : parent
            fields     : individual
            similars   : []

        # Create for the given parent field
        parent.fields[parentField] = [] unless parent.fields[parentField]?
        

        if index == -1
            # Attachs the new element to its parent            
            parent.fields[parentField].push individual
        else
            delete @master
            # Update the new element with an Individual class            
            parent.fields[parentField][index] = individual

        # Add it to the list using $scope.new
        $scope.addIndividual()  


    # Change the scrollIdx to scroll to the given individual
    $scope.scrollTo = (individual)->
        index = -1
        # Looks for individual that match with the given one
        _.each $scope.individuals, (i, idx)-> index = idx if i == individual
        # Update the scrollIdx
        $scope.scrollIdx = index


    $scope.toggleReduce = (individual)->
        individual.reduce = not individual.reduce
    

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

    # Return a unique color with the given string
    $scope.strToColor = strToColor = (str="", lum=-0.4) ->
        # @src http://www.sitepoint.com/javascript-generate-lighter-darker-color/
        colorLuminance = (hex, lum) ->
            # validate hex string
            hex = String(hex).replace(/[^0-9a-f]/g, "")
            hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2]  if hex.length < 6            
            # convert to decimal and change luminosity
            colour = "#"
            for i in [0..2]
                c = parseInt(hex.substr(i * 2, 2), 16)
                c = Math.round(Math.min(Math.max(0, c + (c * lum)), 255)).toString(16)
                colour += ("00" + c).substr(c.length)                
            colour

        # @src http://stackoverflow.com/questions/3426404/create-a-hexadecimal-colour-based-on-a-string-with-jquery-javascript
        generateColor = (str)->    
            i = hash = 0
            while i < str.length
                # str to hash
                hash = str.charCodeAt(i++) + ((hash << 5) - hash)

            colour = "#"
            for i in [0..2]
                # int/hash to hex
                colour += ("00" + ((hash >> i++ * 8) & 0xFF).toString(16)).slice(-2)                 
            colour

        # Combinate color generation and brightness
        colorLuminance( generateColor( md5(str) ), lum)

    # ──────────────────────────────────────────────────────────────────────────
    # Scope watchers
    # ──────────────────────────────────────────────────────────────────────────
    
    # When we update scrollIdx, reset its value after 
    # a short delay to allow scroll again
    $scope.$watch "scrollIdx", => 
        setTimeout =>
            $scope.scrollIdx = -1
            $scope.$apply()
        , 1200

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
        $scope.scrollIdx = $scope.loadIndividual $routeParams.type, $routeParams.id
    else
        # Index of the individual where to scroll 
        $scope.scrollIdx  = -1



ContributeCtrl.$inject = ['$scope', '$routeParams', '$rootScope', 'Individual', 'User']
