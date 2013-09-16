class HomeCtrl
    # Injects dependancies    
    @$inject: ['$scope', 'Page']
    constructor: (@scope, @Page)->
    	# Set page title with no title-case
    	@Page.setTitle("Thematics overview", false)

angular.module('detective').controller 'homeCtrl', HomeCtrl