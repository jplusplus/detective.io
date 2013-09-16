class PageCtrl
    # Injects dependancies    
    @$inject: ['$scope', 'Page']

    constructor: (@scope, @Page)->
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────  
        @scope.Page = @Page

angular.module('detective').controller 'pageCtrl', PageCtrl