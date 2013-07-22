HeaderCtrl = ($scope, $element)->  
HeaderCtrl.$inject = ['$scope', '$element'];

LandingAllCtrl = ($scope)-> 
LandingAllCtrl.$inject = ['$scope']

LandingEnergyCtrl = ($scope)->
LandingEnergyCtrl.$inject = ['$scope']

ContributeCtrl = ($scope, $routeParams)-> 
	$scope.topic = $routeParams.topic
	# Every happended inviduals
	$scope.individuals = [{name:"Datawrapper", type: "project", owners: [{name:"ABZV"}]}]
	#$scope.individuals = []
	# A new individual for kick-star forms
	$scope.new = 
		type: ""
		name: ""	

	# When user submit a kick-start individual form
	$scope.addIndividual = ->
		$scope.individuals.push $scope.new

	$scope.removeIndividual = (index=0)->
		$scope.individuals.splice(index, 1) if $scope.individuals[index]?

	$scope.addMore = (individual, key)->		
		individual[key] = [] unless individual[key]?
		individual[key].push(name:"")

ContributeCtrl.$inject = ['$scope', '$routeParams']
