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
		# Clones the object to avoid inserting duplicates
		o = $.extend(true, {}, $scope.new)
		$scope.individuals.push(o)
		# Disable kickStart form
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

ContributeCtrl.$inject = ['$scope', '$routeParams', '$rootScope']
