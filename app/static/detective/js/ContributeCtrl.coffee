ContributeCtrl = ($scope, $routeParams, $rootScope, Individual)-> 
    $scope.topic = $routeParams.topic
    # By default, hide the kick-start form
    $scope.showKickStart = false
    
    $scope.individuals = []
    # Load an individual for test
    Individual.get {type: "project", id:36}, (project)->        
        # Every happended inviduals
        $scope.individuals = [
            type: "project"
            saved: false
            fields: project
        ]

    # A new individual for kick-star forms
    (initNewIndividual = ->
        $scope.new = 
            type: ""
            saved: false
            fields : new Individual name: ""
    # Self initiating function
    )()

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

    $scope.removeOne = (individual, key, index)->
        if individual.fields[key][index]?
            delete individual.fields[key][index]
            individual.fields[key].splice(index, 1) 

    $scope.toggleReduce = (individual)->
        individual.reduce = not individual.reduce

    $scope.save = (individual)->
        individual.fields.$save(type: individual.type)

ContributeCtrl.$inject = ['$scope', '$routeParams', '$rootScope', 'Individual']
