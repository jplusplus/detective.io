HeaderCtrl = ($scope, $element)->  
HeaderCtrl.$inject = ['$scope', '$element'];

LandingAllCtrl = ($scope)-> 
LandingAllCtrl.$inject = ['$scope']

LandingEnergyCtrl = ($scope)->
LandingEnergyCtrl.$inject = ['$scope']

ContributeCtrl = ($scope, $routeParams, $rootScope)-> 
	$scope.topic = $routeParams.topic
	# By default, hide the kick-start form
	$scope.showKickStart = false
	# Every happended inviduals
	$scope.individuals = [{name:"Datawrapper", type: "project", owner: [{name:"ABZV"}]}]
	#$scope.individuals = []
	# A new individual for kick-star forms
	$scope.new = 
		type: ""
		name: ""

	# When user submit a kick-start individual form
	$scope.addIndividual = (scroll=true)->
		index = $scope.individuals.push($scope.new) - 1
		$scope.showKickStart = false

	$scope.removeIndividual = (index=0)->
		$scope.individuals.splice(index, 1) if $scope.individuals[index]?

	$scope.addOne = (individual, key)->		
		individual[key] = [] unless individual[key]?
		individual[key].push(name:"")

	$scope.removeOne = (individual, key, index)->
		if individual[key][index]?
			delete individual[key][index]
			individual[key].splice(index, 1) 

	$scope.toggleReduce = (individual)->
		individual.reduce = not individual.reduce

	"""
	# Watch individuals to scroll to the new one
	$scope.$watch("individuals", (newValue, oldValue)->
		# New individuals
		if newValue.length > oldValue.length
			# Scroll to the new element
			$(window).scrollTo ".individual:last", 600 
	, true)
	"""

ContributeCtrl.$inject = ['$scope', '$routeParams', '$rootScope']
