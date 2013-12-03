class HomeCtrl
    # Injects dependancies
    @$inject: ['$scope', 'Page']
    constructor: (@scope, @Page)->
    	# Set page title with no title-case
    	@Page.title "Structure your investigation and mine your data", false


angular.module('detective').controller 'homeCtrl', HomeCtrl