class TourCtrl
    # Injects dependencies
    @$inject: ['$scope', 'Page', "Common"]
    constructor: (@scope, @Page, @Common)->
        # Set page title with no title-case
        @Page.title "Structure your investigation and mine your data", false
        # Get all featured topics
        @Common.cachedQuery {type: 'topic', featured: 1}, (d)=> @scope.featured = d

angular.module('detective.controller').controller 'tourCtrl', TourCtrl